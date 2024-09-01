from datetime import datetime
from typing import List
from pydantic import BaseModel


class CreateDocument(BaseModel):
    rubrics: List[str]
    text: str
    created_date: datetime


class ESDocumentModel(BaseModel):
    id: int
    text: str

    class Config:
        strict = True
        from_attributes = True


class Document(BaseModel):
    id: int
    rubrics: List[str]
    text: str
    created_date: datetime

    class Config:
        strict = True
        from_attributes = True