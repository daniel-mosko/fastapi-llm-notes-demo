import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.notes import Notes, NotesContentEmbeddings


@pytest.mark.anyio
async def test_root(ac: AsyncClient):
    response = await ac.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_note_via_api(ac: AsyncClient, db: AsyncSession):
    response = await ac.post(
        f"{settings.api_prefix}/notes/",
        json={
            "title": "Test Note",
            "content": "This is a test note content.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note content."
    assert "id" in data
    assert "hash" in data

    # Fetch from DB and verify
    result = await db.execute(select(Notes).where(Notes.id == data["id"]))
    db_note = result.scalar_one_or_none()

    assert db_note is not None
    assert db_note.title == "Test Note"
    assert db_note.content == "This is a test note content."
    assert db_note.id == data["id"]
    assert db_note.hash == data["hash"]

    # Fetch embedding from DB and verify
    embedding_result = await db.execute(
        select(NotesContentEmbeddings).where(
            NotesContentEmbeddings.note_id == data["id"]
        )
    )
    db_embedding = list(embedding_result.scalars().all())
    print(db_embedding)
    assert len(db_embedding) > 0
