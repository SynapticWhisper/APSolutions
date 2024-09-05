"""
This module defines Pydantic models used for document creation, storage, and integration with
Elasticsearch.

The module includes the following models:
- `CreateDocument`:     Used for validating and creating new document data.
- `ESDocumentModel`:    Represents a document stored in Elasticsearch with an ID and text.
- `DocumentSchema`:     Represents a document stored in the database, including its ID, rubrics, 
                        text, and creation date.

Each model is designed to ensure data integrity and consistency, leveraging Pydantic's validation
features.
The `Config` class in `ESDocumentModel` and `DocumentSchema` ensures strict type checking and
compatibility with ORM models.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, field_validator


class CreateDocument(BaseModel):
    rubrics: List[str]
    text: str
    created_date: datetime

    @field_validator('created_date')
    def remove_timezone(cls, value):
        if value.tzinfo is not None:
            return value.replace(tzinfo=None)
        return value


class ESDocumentModel(BaseModel):
    id: int
    text: str

    class Config:
        strict = True
        from_attributes = True


class DocumentSchema(BaseModel):
    id: int
    rubrics: List[str]
    text: str
    created_date: datetime

    class Config:
        strict = True
        from_attributes = True
