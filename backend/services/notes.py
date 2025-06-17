from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Link, Note
from db.schemas import NoteCreateRequest

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/notes/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/notes/")
def get_all_notes(db: Session = Depends(get_db)):
    return db.query(Note).all()


@router.post("/notes/")
def create_note(note: NoteCreateRequest, db: Session = Depends(get_db)):
    db_note = Note(title=note.title, content_markdown=note.content_markdown)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteCreateRequest, db: Session = Depends(get_db)):
    note = Note(title=note.title, content_markdown=note.content_markdown)

    db_note = db.get(Note, note_id)

    if db_note:
        db_note.title = note.title
        db_note.content_markdown = note.content_markdown
    else:
        raise HTTPException(status_code=404, detail="Note not found")

    db.commit()
    db.refresh(db_note)
    return db_note


@router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.query(Link).filter(
        (Link.source_page_id == note_id) | (Link.target_page_id == note_id)
    ).delete(synchronize_session=False)

    db.delete(db_note)
    db.commit()

    return {"message": f"Note with ID {note_id} and its links deleted successfully"}
