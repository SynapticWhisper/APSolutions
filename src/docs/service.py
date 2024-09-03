from typing import List, Optional
import elastic_transport
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.docs import models
from src.docs.schemas import CreateDocument, ESDocumentModel
from src.docs.es_service import AsyncESClient


class DocumentCRUD:
    def __init__(self, session=Depends(get_async_session)):
        self.__session: AsyncSession = session
        self.__es_search = AsyncESClient()

    async def create(self, document: CreateDocument) -> JSONResponse:
        new_document = models.Document(
            **document.model_dump()
        )
        try:
            self.__session.add(new_document)
            await self.__session.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        else:
            await self.__es_search.add_document(ESDocumentModel(id=new_document.id, text=new_document.text))
            return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Document created successfully"})

    async def create_many(self, doc_list: List[CreateDocument]) -> JSONResponse:
        if not doc_list:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Northing to add"})
        new_docs_list = [
            models.Document(**document.model_dump()) for document in doc_list
        ]
        try:
            self.__session.add_all(new_docs_list)
            await self.__session.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        else:
            await self.__es_search.add_many(
                [ESDocumentModel(id=new_document.id, text=new_document.text) for new_document in new_docs_list]
            )
            return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Documents created successfully"})

    async def __get_by_id(self, document_id: int) -> models.Document:
        stmt = (
            select(models.Document)
            .where(models.Document.id == document_id)
        )
        document: Optional[models.Document] = (await self.__session.execute(stmt)).scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return document

    async def __get_many(self, documents_ids: Optional[List[int]], limit: int) -> Optional[List[models.Document]]:
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
        documnents: Optional[List[models.Document]] = (await self.__session.execute(stmt)).scalars().all()
        return documnents
    
    async def search_and_get_many(self, query: str, limit: int = 20) -> Optional[List[models.Document]]:
        try:
            document_ids = [doc_id async for doc_id in self.__es_search.search_documents(query)]
            documents = await self.__get_many(document_ids, limit)
            return documents
        except elastic_transport.ConnectionError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def __update(self):
        ...

    async def delete(self, document_id: int) -> HTTPException:
        document = await self.__get_by_id(document_id)
        await self.__session.delete(document)
        await self.__session.commit()
        await self.__es_search.delete_document(document_id)
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT)
