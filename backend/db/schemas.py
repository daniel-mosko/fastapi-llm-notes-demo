from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# --- Link Models ---


class LinkSchema(BaseModel):
    """
    Base schema for Link attributes shared across different operations.
    """

    source_page_id: int
    target_page_id: int


class LinkCreateRequest(LinkSchema):
    """
    Schema for creating a new Link.
    This is what you expect in the request body when a client wants to create a link.
    """

    pass  # No additional fields needed for creation beyond LinkSchema


class LinkResponse(LinkSchema):
    """
    Schema for reading/returning a Link.
    This is what your API will send back to the client as a representation of a link.
    """

    # If Link had its own 'id' in the DB, it would go here.
    # For now, it inherits directly from LinkSchema and just needs the ORM config.
    class Config:
        from_attributes = True


# --- Note Models ---


class NoteSchema(BaseModel):
    """
    Base schema for Note attributes shared across different operations.
    """

    title: str
    content_markdown: str


class NoteCreateRequest(BaseModel):
    """
    Schema for creating a new Note.
    This is specifically for the POST request body.
    Content is optional on creation here, which deviates from NoteSchema,
    so it's a separate model.
    """

    title: str
    content_markdown: Optional[str] = None


class NoteResponse(NoteSchema):
    """
    Schema for reading/returning a Note.
    This is what your API will send back to the client.
    It includes database-generated fields like 'id', 'created_at', 'updated_at',
    and related resources like links.
    """

    id: int
    created_at: datetime
    updated_at: datetime
    outgoing_links: Optional[List[LinkResponse]] = []
    incoming_links: Optional[List[LinkResponse]] = []

    class Config:
        from_attributes = True
