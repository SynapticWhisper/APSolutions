
from typing import List, Optional

from fastapi import FastAPI, UploadFile, HTTPException, status, Depends

from src.docs.schemas import CreateDocument
from src.docs.router import router as DocumnetRouter
from src.docs.service import DocumentCRUD
from src.tools import download_from_yadisk, download_file, get_documnets
# from elasticsearch import AsyncElasticsearch
# from src.database import get_async_session
# from src.docs.es_service import AsyncESClient
# es = AsyncElasticsearch()

# @app.on_event("shutdown")
# async def app_shutdown():
#     await es.close()

app = FastAPI()

app.include_router(DocumnetRouter)

@app.post("/import_data_from_csv")
async def import_data_from_csv(
    csv_file: Optional[UploadFile] = None,
    ya_disk_url: Optional[str] = None,
    service: DocumentCRUD = Depends()
):
    if not csv_file and not ya_disk_url:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Neither file nor link were transferred"})
    elif ya_disk_url:
        file = await download_from_yadisk(ya_disk_url)
    else:
        file = await download_file(csv_file)

    documnets_to_add: List[CreateDocument] = get_documnets(file)
    await service.create_many(documnets_to_add)
