from datetime import datetime

from pydantic import BaseModel

from app.models.notice import NoticeCategory


class NoticeCreate(BaseModel):
    title: str
    body: str
    category: NoticeCategory = NoticeCategory.general


class NoticeOut(BaseModel):
    id: int
    title: str
    body: str
    category: NoticeCategory
    author_name: str
    created_at: datetime