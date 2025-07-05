import re
from typing import Any, List

import numpy as np
from backend.models.notes import Notes, NotesContentEmbeddings
from backend.schemas.notes import (
    BaseNoteSchema,
    NoteResponseSchema,
    PromptSchema,
    SimilarNotesSchema,
)
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


async def get_similar_notes(
    query_embeddings: List[Any],
    db_sentence_embeddings: List[NotesContentEmbeddings],
    db: AsyncSession,
    top_k=5,
) -> List[NoteResponseSchema]:
    """
    query_embeddings: numpy array (m x d), m sentences in query note
    db_sentence_embeddings: list of objects with .embedding (d,), .note_id
    """
    from collections import defaultdict

    import torch

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
    ]  # Split by end of sentences (.!?)
    sentences = np.array(
        [(start_index, sentence.strip()) for start_index, sentence in matches]
    )

    model.max_seq_length = len(
        max(sentences[:, 1], key=len)
    )  # So that max len sentence can be encoded correctly

    # (idx, vec)
    embeddings = model.encode(sentences[:, 1])
    return (
        list(map(int, sentences[:, 0])),
        [len(sen) for sen in sentences[:, 1]],
        embeddings.tolist(),
    )
