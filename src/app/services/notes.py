import re
from collections import defaultdict
from typing import Any

import numpy as np
import torch
from fastapi import HTTPException, status
from sentence_transformers import SentenceTransformer
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notes import Notes, NotesContentEmbeddings
from app.schemas.notes import (
    BaseNoteSchema,
    NoteResponseSchema,
    PromptSchema,
    SimilarNotesSchema,
)
from app.utils.hashing import compute_note_hash, hash_has_changed

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


async def create_note(note: BaseNoteSchema, db: AsyncSession) -> Notes:
    new_note = Notes(
        title=note.title, content=note.content, hash=compute_note_hash(note)
    )
    db.add(new_note)

    try:
        await db.commit()
        await db.refresh(new_note)
        await create_embedding(new_note, db)
        return new_note
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating note: {e!s}",
        )


async def get_note_by_id(note_id: int, db: AsyncSession) -> Notes:
    note = await db.get(Notes, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


async def get_all_notes(db: AsyncSession) -> list[Notes]:
    result = await db.execute(select(Notes))
    notes = list(result.scalars().all())
    return notes


async def update_note(
    note_id: int, note: BaseNoteSchema, db: AsyncSession
) -> Notes:
    updated_note = Notes(title=note.title, content=note.content)

    db_note = await db.get(Notes, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    if hash_has_changed(updated_note, db_note):
        await create_embedding(updated_note, db)
        db_note.hash = compute_note_hash(updated_note)

    db_note.title = updated_note.title
    db_note.content = updated_note.content

    try:
        await db.commit()
        await db.refresh(db_note)
        return db_note
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating the note: {e!s}",
        )


async def delete_note_by_id(note_id: int, db: AsyncSession):
    try:
        await db.execute(
            delete(NotesContentEmbeddings).where(
                NotesContentEmbeddings.note_id == note_id
            )
        )

        db_note = await db.get(Notes, note_id)
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")

        await db.delete(db_note)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting note: {e!s}",
        )


async def get_similar_notes(
    query_embeddings: list[Any],
    db_sentence_embeddings: list[NotesContentEmbeddings],
    db: AsyncSession,
    top_k=5,
) -> list[NoteResponseSchema]:
    """
    query_embeddings: numpy array (m x d), m sentences in query note
    db_sentence_embeddings: list of objects with .embedding (d,), .note_id
    """
    # Convert to tensors
    query_tensor = torch.tensor(query_embeddings)  # (m, d)
    db_embeddings_list = [emb.embedding for emb in db_sentence_embeddings]
    db_note_ids = [emb.note_id for emb in db_sentence_embeddings]
    db_tensor = torch.tensor(np.array(db_embeddings_list))  # (n, d)

    # Cosine similarity between query sentences and all db sentences: (m, n)
    sim_matrix = torch.matmul(query_tensor, db_tensor.T)

    # Aggregate per DB sentence’s note:
    note_to_sims = defaultdict(list)
    for db_idx, note_id in enumerate(db_note_ids):
        sims_for_db_sentence = sim_matrix[
            :, db_idx
        ]  # similarity of all query sentences to this DB sentence
        max_sim = (
            sims_for_db_sentence.max().item()
        )  # max similarity across query sentences
        note_to_sims[note_id].append(max_sim)

    # Aggregate similarities per note, e.g., average max similarity of all sentences of that note
    note_scores = {
        note_id: sum(sims) / len(sims) for note_id, sims in note_to_sims.items()
    }

    sorted_notes = sorted(
        note_scores.items(), key=lambda x: x[1], reverse=True
    )[:top_k]

    # fetch notes from db
    similar_notes = []
    for note_id, score in sorted_notes:
        note = await db.get(Notes, note_id)
        if note:
            note_response = NoteResponseSchema.model_validate(note)
            similar_notes.append(
                SimilarNotesSchema(note=note_response, score=score)
            )

    return similar_notes


async def create_embedding(note: Notes, db: AsyncSession):
    """Split note to chunks, create embeddings and push to DB"""
    chunk_ids, sentences_len, note_embeddings = get_embedding(note)

    # Add all chunks embeddings to DB
    for i in range(len(chunk_ids)):
        note_content_embedding = NotesContentEmbeddings(
            note_id=note.id,
            chunk_index=i,
            embedding=note_embeddings[i],
            chunk_start_position=chunk_ids[i],
            chunk_end_position=chunk_ids[i] + sentences_len[i],
        )

        db.add(note_content_embedding)
        try:
            await db.commit()
            await db.refresh(note_content_embedding)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating note embedding: {e!s}",
            )


def get_embedding(
    query: Notes | BaseNoteSchema | PromptSchema,
) -> tuple[list[int], list[int], list[Any]]:
    """
    Split note to chunks, create embeddings using sentence sentence-transformers
    returns chunk_ids, sentences_len, note_embeddings
    """

    text_to_embed: str
    if isinstance(query, Notes) or isinstance(query, BaseNoteSchema):
        text_to_embed = (f"{query.title}. {query.content}").lower()
    else:
        text_to_embed = (query.message).lower()

    matches = [
        (m.start(), m.group(0).strip())
        for m in re.finditer(r"[^.!?]+", text_to_embed)
    ]
    sentences = np.array(
        [(start_index, sentence.strip()) for start_index, sentence in matches]
    )

    model.max_seq_length = len(max(sentences[:, 1], key=len))

    # (idx, vec)
    embeddings = model.encode(sentences[:, 1])
    return (
        list(map(int, sentences[:, 0])),
        [len(sen) for sen in sentences[:, 1]],
        embeddings.tolist(),
    )
