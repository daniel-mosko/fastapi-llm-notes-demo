import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LinkSchema(BaseModel):
    source_note_id: int
    target_note_id: int


class BaseNoteSchema(BaseModel):
    title: str
    content: str


class NoteResponseSchema(BaseNoteSchema):
    id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    hash: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SimilarNotesSchema(BaseModel):
    note: NoteResponseSchema
    score: float
