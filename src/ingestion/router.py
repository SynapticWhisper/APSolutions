from typing import Optional
from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from src.ingestion.tools import download_file, download_from_yadisk, import_csv


router = APIRouter()


@router.post("/upload-from-file", response_class=JSONResponse)
async def upload_from_file(
    file: UploadFile,
    separator: Optional[str] = ","
):
    file_path: str = await download_file(file)
    return await import_csv(file_path, sep=separator)


@router.post("/upload-from-yandex-disk", response_class=JSONResponse)
async def upload_from_yandex_disk(
    disk_link: str,
    separator: Optional[str] = ","
):
    file_path: str = await download_from_yadisk(disk_link)
    return await import_csv(file_path, sep=separator)
    