"""
Module functionality: Provides endpoints for uploading documents to the database 
from a file or a Yandex Disk link.
"""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse

from src.docs.service import DocumentCRUD
from src.ingestion.tools import download_file, download_from_yadisk, import_csv


router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"]
)


@router.post("/upload-from-file", response_class=JSONResponse)
async def upload_from_file(
    file: UploadFile,
    separator: Optional[str] = ",",
    service: DocumentCRUD = Depends()
):
    """
    Uploads document data from a user-uploaded file to the database.

    Args:
        file (UploadFile): The file uploaded by the user.
        separator (Optional[str]): The delimiter used in the CSV file. Defaults to a comma (",").
        
    Returns:
        JSONResponse: A response indicating the success of the operation.
    """
    file_path: str = await download_file(file)
    return await import_csv(file_path, sep=separator, service=service)


@router.post("/upload-from-yandex-disk", response_class=JSONResponse)
async def upload_from_yandex_disk(
    disk_link: str,
    separator: Optional[str] = ",",
    service: DocumentCRUD = Depends()
):
    """
    Uploads document data from a file on Yandex Disk to the database.

    Args:
        disk_link (str): The public link to the file on Yandex Disk.
        separator (Optional[str]): The delimiter used in the CSV file. Defaults to a comma (",").

    Returns:
        JSONResponse: A response indicating the success of the operation.
    """
    file_path: str = await download_from_yadisk(disk_link)
    return await import_csv(file_path, sep=separator, service=service)
    