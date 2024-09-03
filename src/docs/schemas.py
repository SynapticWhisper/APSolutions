"""Module functionality ..."""

from datetime import datetime
from typing import List
from pydantic import BaseModel


class CreateDocument(BaseModel):
    """Create document pydantic model."""
    rubrics: List[str]
    text: str
    created_date: datetime


class ESDocumentModel(BaseModel):
    """ElasticSearch document pydantic model."""
    id: int
    text: str

    class Config:
        """Configuration class."""
        strict = True
        from_attributes = True


class DocumentSchema(BaseModel):
    """Document pydantic model."""
    id: int
    rubrics: List[str]
    text: str
    created_date: datetime

    class Config:
        """Configuration class."""
        strict = True
        from_attributes = True
