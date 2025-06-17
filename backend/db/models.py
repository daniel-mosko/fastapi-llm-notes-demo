from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationship to links where this page is the source
    outgoing_links = relationship(
        "Link", back_populates="source_page", foreign_keys="Link.source_page_id"
    )
    # Relationship to links where this page is the target
    incoming_links = relationship(
        "Link", back_populates="target_page", foreign_keys="Link.target_page_id"
    )


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)

    source_page_id = Column(Integer, ForeignKey("notes.id"), nullable=True)
    target_page_id = Column(Integer, ForeignKey("notes.id"), nullable=True)

    source_page = relationship(
        "Note", back_populates="outgoing_links", foreign_keys=[source_page_id]
    )
    target_page = relationship(
        "Note", back_populates="incoming_links", foreign_keys=[target_page_id]
    )
