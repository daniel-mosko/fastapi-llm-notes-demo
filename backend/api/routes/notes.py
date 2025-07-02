import uuid
from typing import List

from backend.db.database import SessionLocal
from backend.db.models import Notes, NotesContentEmbeddings
from backend.db.schemas import BaseNoteSchema, NoteResponseSchema, SimilarNotesSchema
from backend.services.sentence_processing import get_note_embedding, get_similar_notes
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/notes", tags=["notes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{note_id}", response_model=NoteResponseSchema)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Notes, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/", response_model=List[NoteResponseSchema])
def get_all_notes(db: Session = Depends(get_db)):
    return db.query(Notes).all()


@router.post("/", response_model=NoteResponseSchema)
def create_note(note: BaseNoteSchema, background_tasks:BackgroundTasks, db: Session = Depends(get_db)):
    db_note = Notes(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Schedule the create_embedding function to run in the background
    background_tasks.add_task(create_embedding,db_note,db)

    return db_note

def create_embedding(note:Notes, db: Session):
    chunk_ids,sentences_len, note_embeddings = get_note_embedding(note)

    for i in range(len(chunk_ids)):
        note_content_embedding = NotesContentEmbeddings(
            note_id = note.id,
            chunk_index = i,
            embedding = note_embeddings[i],
            chunk_start_position = chunk_ids[i],
            chunk_end_position = chunk_ids[i] + sentences_len[i]
        )

        db.add(note_content_embedding)
        db.commit()
        db.refresh(note_content_embedding)

@router.put("/{note_id}", response_model=NoteResponseSchema)
def update_note(note_id: int, note: BaseNoteSchema, db: Session = Depends(get_db)):
    db_note = Notes(title=note.title, content=note.content)

    db_note = db.get(Notes, note_id)

    if db_note:
        db_note.title = note.title
        db_note.content = note.content
    else:
        raise HTTPException(status_code=404, detail="Note not found")

    db.commit()
    db.refresh(db_note)
    return db_note

@router.post("/search", response_model=List[SimilarNotesSchema])
def similar_note(note: BaseNoteSchema, db: Session = Depends(get_db)):
    _, _, note_embedding = get_note_embedding(note)
    db_embeddings = db.query(NotesContentEmbeddings).all()

    similar_notes= get_similar_notes(note_embedding,db_embeddings, db)
    return similar_notes


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: uuid.UUID, db: Session = Depends(get_db)):
    db.query(NotesContentEmbeddings).filter(NotesContentEmbeddings.note_id == note_id).delete()

    db_note = db.query(Notes).filter(Notes.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

