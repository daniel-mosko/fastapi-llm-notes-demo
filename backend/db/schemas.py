from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class LinkBase(BaseModel):
    source_page_id: int
    target_page_id: int


class LinkCreate(LinkBase):
    pass


class LinkRead(LinkBase):
    class Config:
        orm_mode = True


class PageBase(BaseModel):
    title: str
    content_markdown: str


class PageCreate(PageBase):
    pass


class PageRead(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    outgoing_links: Optional[List[LinkRead]] = []
    incoming_links: Optional[List[LinkRead]] = []

    class Config:
        orm_mode = True
