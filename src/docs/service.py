from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.docs import models
from src.docs.schemas import CreateDocument


class DocumnetCRUD:
    def __init__(self, session=Depends(get_async_session)):
        self.__session: AsyncSession = session

    async def create(self, document: CreateDocument) -> HTTPException:
        new_document = models.Document(
            **document.model_dump()
        )
        try:
            self.__session.add(new_document)
            await self.__session.commit()
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return HTTPException(status_code=status.HTTP_201_CREATED)

    async def __get_by_id(self, document_id: int) -> models.Document:
        stmt = (
            select(models.Document)
            .where(models.Document.id == document_id)
        )
        document: Optional[models.Document] = (await self.__session.execute(stmt)).scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return document

    async def get_many(self, document_ids: List[int], limit: int = 20) -> Optional[List[models.Document]]:
        stmt = (
            select(models.Document)
            .where(models.Document.id in document_ids)
            .limit(limit)
            .order_by(
                asc(models.Document.created_date)
            )
        )

        documnents: Optional[List[models.Document]] = (await self.__session.execute(stmt)).scalars().all()
        return documnents
    
    async def __update(self):
        ...

    async def delete(self, document_id: int) -> HTTPException:
        document = await self.__get_by_id(document_id)
        await self.__session.delete(document)
        await self.__session.commit()
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT)