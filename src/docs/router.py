from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.docs.schemas import DocumentSchema
from src.docs.service import DocumentCRUD

router = APIRouter(
    prefix="/docs",
    tags=["Documents"]
)


@router.get("/search", response_model=List[DocumentSchema])
async def get_documents(
    query: str,
    limit: int = 20,
    service: DocumentCRUD = Depends()
):
    return await service.search_and_get_many(query=query, limit=limit)


@router.delete("/delete/{document_id}", response_class=JSONResponse)
async def delete_documnet(
    document_id: int,
    service: DocumentCRUD = Depends()
):
    return await service.delete(document_id)