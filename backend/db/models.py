from datetime import datetime, timezone

from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class Page(Base):
    __tablename__ = "pages"

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

    source_page_id = Column(Integer, ForeignKey("pages.id"), primary_key=True)
    target_page_id = Column(Integer, ForeignKey("pages.id"), primary_key=True)

    source_page = relationship(
        "Page", foreign_keys=[source_page_id], back_populates="outgoing_links"
    )
    target_page = relationship(
        "Page", foreign_keys=[target_page_id], back_populates="incoming_links"
    )
