import datetime
from typing import Any, List, Optional

from pgvector.sqlalchemy.vector import VECTOR
from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Notes(Base):
    __tablename__ = "notes"
    __table_args__ = (PrimaryKeyConstraint("id", name="notes_pkey"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True), server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True), server_default=text("CURRENT_TIMESTAMP")
    )

    notes_content_embeddings: Mapped[List["NotesContentEmbeddings"]] = (
        relationship("NotesContentEmbeddings", back_populates="note")
    )


class NotesContentEmbeddings(Base):
    __tablename__ = "notes_content_embeddings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["note_id"],
            ["notes.id"],
            ondelete="CASCADE",
            name="notes_content_embeddings_note_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="notes_content_embeddings_pkey"),
        UniqueConstraint(
            "note_id",
            "chunk_index",
            name="notes_content_embeddings_note_id_chunk_index_key",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer)
    chunk_index: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[Optional[Any]] = mapped_column(VECTOR(384))
    chunk_start_position: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_end_position: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(True), server_default=text("CURRENT_TIMESTAMP")
    )

    note: Mapped["Notes"] = relationship(
        "Notes", back_populates="notes_content_embeddings"
    )
