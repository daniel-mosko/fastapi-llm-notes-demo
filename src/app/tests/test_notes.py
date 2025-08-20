from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import settings
from app.main import app


@pytest.fixture(scope="module")
async def ac() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000"
    ) as ac:
        yield ac


@pytest.mark.anyio
async def test_root(ac: AsyncClient):
    response = await ac.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_note_via_api(ac: AsyncClient):
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


# @pytest.mark.anyio
# async def test_create_note(client: TestClient, db: AsyncSession):
#     """Test creating a new note and verifying it's stored correctly."""
#     # Arrange
#     note_data = BaseNoteSchema(
#         title="Test Note", content="This is a test note content."
#     )
#
#     # Act
#     new_note = await create_note(note_data, db)
#
#     # Assert - Verify the created note
#     assert new_note.id is not None
#     assert new_note.title == "Test Note"
#     assert new_note.content == "This is a test note content."
#     assert new_note.hash == "temp_hash"  # Consider if this should be dynamic
#
#     # Assert - Verify persistence by fetching from database
#     fetched_note = await get_note_by_id(new_note.id, db)
#     assert fetched_note is not None
#     assert fetched_note.id == new_note.id
#     assert fetched_note.title == new_note.title
#     assert fetched_note.content == new_note.content
#     assert fetched_note.hash == new_note.hash
