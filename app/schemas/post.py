from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    file_url: Optional[str] = None

class PostUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    file_url: Optional[str] = None

class Post(BaseModel):
    id: int
    content: str
    user_id: int
    username: str
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    file_url: Optional[str] = None

    class Config:
        from_attributes = True
