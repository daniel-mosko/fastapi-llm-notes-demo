from typing import List

import httpx
from app.ai.chat_requests import handle_gemini_request
from app.ai.prompt_templates import (
    ask_from_similar_notes_prompt,
    summarize_prompt,
)
from app.api.deps import get_db_session
from app.config.logger import get_logger
from app.models.notes import Notes, NotesContentEmbeddings
from app.schemas.notes import (
    BaseNoteSchema,
    NoteResponseSchema,
    PromptSchema,
    SimilarNotesSchema,
    SummarizeNotesSchema,
)
from app.services.notes import get_embedding, get_similar_notes
from app.utils.hashing import compute_note_hash, hash_has_changed
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/{note_id}", response_model=NoteResponseSchema)
async def get_note_by_id(
    note_id: int, db: AsyncSession = Depends(get_db_session)
):
    """Get note from DB by id"""
    note = await db.get(Notes, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/", response_model=List[NoteResponseSchema])
async def get_all_notes(db: AsyncSession = Depends(get_db_session)):
    """Get all notes from DB"""
    result = await db.execute(select(Notes))
    notes = result.scalars()
    return notes


@router.post("/", response_model=NoteResponseSchema)
async def create_note(
    note: BaseNoteSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
):
    """Post new note to DB"""
    new_note = Notes(
        title=note.title, content=note.content, hash=compute_note_hash(note)
    )
    db.add(new_note)

    try:
        await db.commit()
        await db.refresh(new_note)

        background_tasks.add_task(create_embedding, new_note, db)

        return new_note
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating note: {e!s}",
        )


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


@router.put("/{note_id}", response_model=NoteResponseSchema)
async def update_note(
    note_id: int,
    note: BaseNoteSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
):
    """Update note content or title"""
    updated_note = Notes(title=note.title, content=note.content)

    db_note = await db.get(Notes, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    if hash_has_changed(updated_note, db_note):
        background_tasks.add_task(create_embedding, updated_note, db)
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


@router.post("/search", response_model=List[SimilarNotesSchema])
async def similar_note(
    input_item: BaseNoteSchema | PromptSchema,
    db: AsyncSession = Depends(get_db_session),
):
    """Finds semantically similar notes to input_item [Query or Note] in the database"""
    _, _, note_embedding = get_embedding(input_item)
    result = await db.execute(select(NotesContentEmbeddings))
    db_embeddings = list(result.scalars())

    similar_notes = await get_similar_notes(note_embedding, db_embeddings, db)
    return similar_notes


@router.post("/ask_similar", response_model=SummarizeNotesSchema)
async def ask_from_similar_notes(
    prompt: PromptSchema, db: AsyncSession = Depends(get_db_session)
):
    similar_notes = await similar_note(prompt, db)
    async with httpx.AsyncClient() as client:
        sys_prompt = ask_from_similar_notes_prompt(
            prompt.message, similar_notes
        )
        response = await handle_gemini_request(client, sys_prompt)

    if response:
        return SummarizeNotesSchema(summary=response)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error getting the summary",
    )


@router.post("/summarize", response_model=SummarizeNotesSchema)
async def summarize_note(note: BaseNoteSchema):
    async with httpx.AsyncClient() as client:
        sys_prompt = summarize_prompt(note)
        summary = await handle_gemini_request(client, sys_prompt)

    if summary:
        return SummarizeNotesSchema(summary=summary)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error getting the summary",
    )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_by_id(
    note_id: int, db: AsyncSession = Depends(get_db_session)
):
    try:
        await db.execute(
            delete(NotesContentEmbeddings).where(
                NotesContentEmbeddings.note_id == note_id
            )
        )

        # Get the note using async method
        db_note = await db.get(Notes, note_id)
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Delete the note
        await db.delete(db_note)

        # Commit the transaction
        await db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting note: {e!s}",
        )
