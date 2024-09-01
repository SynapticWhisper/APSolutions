from datetime import datetime
from typing import List
from pydantic import BaseModel


class CreateDocument(BaseModel):
    rubrics: List[str]
    text: str
    created_date: datetime


class CreateManyDocs(BaseModel):
    docs_list: List[CreateDocument]


class Document(BaseModel):
    id: int
    rubrics: List[str]
    text: str
    created_date: datetime

    class Config:
        strict = True
        from_attributes = True