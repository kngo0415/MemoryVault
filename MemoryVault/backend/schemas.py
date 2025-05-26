from pydantic import BaseModel
import datetime

class NoteBase(BaseModel):
    content: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True # For Pydantic v2+ compatibility with SQLAlchemy models
