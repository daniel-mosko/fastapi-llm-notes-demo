import httpx
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chat_requests import handle_gemini_request
from app.ai.prompt_templates import (
    ask_from_similar_notes_prompt,
    summarize_prompt,
)
from app.config.logger import get_logger
from app.core.database import session_manager
from app.models.notes import NotesContentEmbeddings
from app.schemas.notes import (
    BaseNoteSchema,
    NoteResponseSchema,
    PromptSchema,
    SimilarNotesSchema,
    SummarizeNotesSchema,
)
from app.services.notes import (
    create_note,
    delete_note_by_id,
    get_all_notes,
    get_embedding,
    get_note_by_id,
    get_similar_notes,
    update_note,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/{note_id}", response_model=NoteResponseSchema)
async def read_note_by_id(
    note_id: int, db: AsyncSession = Depends(session_manager.get_session)
):
    """Get note from DB by id"""
    return await get_note_by_id(note_id, db)


@router.get("/", response_model=list[NoteResponseSchema])
async def read_all_notes(
    db: AsyncSession = Depends(session_manager.get_session),
):
    """Get all notes from DB"""
    return await get_all_notes(db)


@router.post("/", response_model=NoteResponseSchema)
async def create_new_note(
    note: BaseNoteSchema,
    db: AsyncSession = Depends(session_manager.get_session),
):
    """Post new note to DB"""
    return await create_note(note, db)


@router.put("/{note_id}", response_model=NoteResponseSchema)
async def update_existing_note(
    note_id: int,
    note: BaseNoteSchema,
    db: AsyncSession = Depends(session_manager.get_session),
):
    """Update note content or title"""
    return await update_note(note_id, note, db)


@router.post("/search", response_model=list[SimilarNotesSchema])
async def similar_note(
    input_item: BaseNoteSchema | PromptSchema,
    db: AsyncSession = Depends(session_manager.get_session),
):
    """Finds semantically similar notes to input_item [Query or Note] in the database"""
    _, _, note_embedding = get_embedding(input_item)
    result = await db.execute(select(NotesContentEmbeddings))
    db_embeddings = list(result.scalars())

    similar_notes = await get_similar_notes(note_embedding, db_embeddings, db)
    return similar_notes


@router.post("/ask_similar", response_model=SummarizeNotesSchema)
async def ask_from_similar_notes(
    prompt: PromptSchema,
    db: AsyncSession = Depends(session_manager.get_session),
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


@router.delete("/{note_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_note(
    note_id: int, db: AsyncSession = Depends(session_manager.get_session)
):
    await delete_note_by_id(note_id, db)
    return Response(status_code=status.HTTP_202_ACCEPTED)
