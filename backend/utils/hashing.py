import hashlib

from backend.models.notes import Notes
from backend.schemas.notes import BaseNoteSchema


def compute_note_hash(note: Notes | BaseNoteSchema) -> str:
    """Compute the MD5 hash of the given content."""
    return hashlib.md5((note.title + ". " + note.content).encode()).hexdigest()


def hash_has_changed(updated_note: Notes, db_note: Notes) -> bool:
    if updated_note.hash is not None:
        return updated_note.hash != db_note.hash
    return compute_note_hash(updated_note) != db_note.hash
