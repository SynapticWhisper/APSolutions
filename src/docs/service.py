"""
This module provides CRUD operations for documents in a database with Elasticsearch integration.

The `DocumentCRUD` class includes methods for creating, reading, and deleting documents in both 
a relational database (via SQLAlchemy) and an Elasticsearch index. The module handles operations 
such as creating single or multiple documents, searching documents in Elasticsearch, and ensuring 
synchronization between the database and Elasticsearch.

Key functionalities include:
- Creating single and multiple documents with automatic indexing in Elasticsearch.
- Searching for documents using Elasticsearch and retrieving them from the database.
- Deleting documents from both the database and Elasticsearch.
- Handling errors such as connection issues and integrity violations.

This module is designed for asynchronous operation, utilizing FastAPI dependencies for database 
sessions and Elasticsearch connectivity.
"""

from typing import List, Optional
import elastic_transport
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.docs import models
from src.docs.schemas import CreateDocument, ESDocumentModel
from src.docs.es_service import AsyncESClient


class DocumentCRUD:
    """
    Provides CRUD operations for the Document model, integrating both database and Elasticsearch
    operations.

    Attributes:
        __session (AsyncSession): The SQLAlchemy asynchronous session for database operations.
        __es_search (AsyncESClient): The Elasticsearch client for document indexing and searching.
    """
    def __init__(self, session=Depends(get_async_session)):
        self.__session: AsyncSession = session
        self.__es_search = AsyncESClient()

    async def create(self, document: CreateDocument) -> JSONResponse:
        """
        Creates a new document in the database and indexes it in Elasticsearch.

        Args:
            document (CreateDocument): The document data to create.

        Returns:
            JSONResponse: A response indicating the success or failure of the operation.

        Raises:
            HTTPException: If an integrity error occurs during the database operation.
        """
        new_document = models.Document(
            **document.model_dump()
        )
        try:
            self.__session.add(new_document)
            await self.__session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
        await self.__es_search.add_document(
            ESDocumentModel(id=new_document.id, text=new_document.text)
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Document created successfully"}
        )

    async def create_many(self, doc_list: List[CreateDocument]) -> JSONResponse:
        """
        Creates multiple documents in the database and indexes them in Elasticsearch.

        Args:
            doc_list (List[CreateDocument]): A list of document data to create.

        Returns:
            JSONResponse: A response indicating the success or failure of the operation.
        """
        if not doc_list:
            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT,
                content={"message": "Northing to add"}
            )
        new_docs_list = [
            models.Document(**document.model_dump()) for document in doc_list
        ]
        try:
            self.__session.add_all(new_docs_list)
            await self.__session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e
        errors = await self.__es_search.add_many(
            [
                ESDocumentModel(
                    id=new_document.id,
                    text=new_document.text
                ) for new_document in new_docs_list
            ]
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": f"Documents created. Errors occurred during execution with {errors} documents"}
        )

    async def __get_by_id(self, document_id: int) -> models.Document:
        """
        Retrieves a document from the database by its ID.

        Args:
            document_id (int): The ID of the document to retrieve.

        Returns:
            models.Document: The retrieved document.

        Raises:
            HTTPException: If the document is not found.
        """
        stmt = (
            select(models.Document)
            .where(models.Document.id == document_id)
        )
        document = (await self.__session.execute(stmt)).scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return document

    async def __get_many(
            self,
            documents_ids: Optional[List[int]],
            limit: int
        ) -> Optional[List[models.Document]]:
        """
        Retrieves multiple documents from the database by their IDs.

        Args:
            documents_ids (Optional[List[int]]): A list of document IDs to retrieve.
            limit (int): The maximum number of documents to retrieve.

        Returns:
            Optional[List[models.Document]]: A list of documents or None if no IDs are provided.
        """
        if not documents_ids:
            return None
        stmt = (
            select(models.Document)
            .where(models.Document.id.in_(documents_ids))
            .limit(limit)
            .order_by(
                desc(models.Document.created_date)
            )
        )
        documents = (await self.__session.execute(stmt)).scalars().all()
        return documents

    async def search_and_get_many(
            self,
            query: str,
            limit: int = 20
        ) -> Optional[List[models.Document]]:
        """
        Searches for documents in Elasticsearch and retrieves them from the database.

        Args:
            query (str): The search query to use in Elasticsearch.
            limit (int, optional): The maximum number of documents to retrieve. Defaults to 20.

        Returns:
            Optional[List[models.Document]]: A list of documents matching the search criteria.

        Raises:
            HTTPException: If there is a connection error with Elasticsearch.
        """
        try:
            document_ids = [doc_id async for doc_id in self.__es_search.search_documents(query, limit=limit)]
            documents = await self.__get_many(document_ids, limit)
            return documents
        except elastic_transport.ConnectionError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    # async def __update(self):
    #     ...

    async def delete(self, document_id: int) -> HTTPException:
        """
        Deletes a document from both the database and Elasticsearch.

        Args:
            document_id (int): The ID of the document to delete.

        Returns:
            HTTPException: A response indicating that the document was successfully deleted.
        """
        try:
            await self.__es_search.delete_document(document_id)
            document = await self.__get_by_id(document_id)
            await self.__session.delete(document)
            await self.__session.commit()
            return HTTPException(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e) from e
