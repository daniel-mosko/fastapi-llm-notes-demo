import datetime
import uuid
from typing import Any, List, Optional

from pgvector.sqlalchemy.vector import VECTOR
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Notes(Base):
    __tablename__ = 'notes'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='notes_pkey'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    notes_content_embeddings: Mapped[List['NotesContentEmbeddings']] = relationship('NotesContentEmbeddings', back_populates='note')
    word_links: Mapped[List['WordLinks']] = relationship('WordLinks', foreign_keys='[WordLinks.source_note_id]', back_populates='source_note')
    word_links_: Mapped[List['WordLinks']] = relationship('WordLinks', foreign_keys='[WordLinks.target_note_id]', back_populates='target_note')


class NotesContentEmbeddings(Base):
    __tablename__ = 'notes_content_embeddings'
    __table_args__ = (
        ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE', name='notes_content_embeddings_note_id_fkey'),
        PrimaryKeyConstraint('id', name='notes_content_embeddings_pkey'),
        UniqueConstraint('note_id', 'chunk_index', name='notes_content_embeddings_note_id_chunk_index_key')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    note_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    chunk_index: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[Optional[Any]] = mapped_column(VECTOR(384))
    chunk_start_position: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_end_position: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    note: Mapped['Notes'] = relationship('Notes', back_populates='notes_content_embeddings')


class WordLinks(Base):
    __tablename__ = 'word_links'
    __table_args__ = (
        CheckConstraint('source_note_id <> target_note_id OR source_position_start <> target_position_start', name='word_links_check'),
        ForeignKeyConstraint(['source_note_id'], ['notes.id'], ondelete='CASCADE', name='word_links_source_note_id_fkey'),
        ForeignKeyConstraint(['target_note_id'], ['notes.id'], ondelete='CASCADE', name='word_links_target_note_id_fkey'),
        PrimaryKeyConstraint('id', name='word_links_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    source_note_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    source_text: Mapped[str] = mapped_column(String(255))
    source_position_start: Mapped[int] = mapped_column(Integer)
    source_position_end: Mapped[int] = mapped_column(Integer)
    target_note_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    target_text: Mapped[str] = mapped_column(String(255))
    target_position_start: Mapped[int] = mapped_column(Integer)
    target_position_end: Mapped[int] = mapped_column(Integer)
    link_type: Mapped[str] = mapped_column(String(50), server_default=text("'reference'::character varying"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    source_note: Mapped['Notes'] = relationship('Notes', foreign_keys=[source_note_id], back_populates='word_links')
    target_note: Mapped['Notes'] = relationship('Notes', foreign_keys=[target_note_id], back_populates='word_links_')



