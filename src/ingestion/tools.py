"""Download csv tools."""

import asyncio
import json
from urllib.parse import urlencode
from typing import List
import pandas as pd
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from httpx import AsyncClient, HTTPStatusError

from src.docs.service import DocumentCRUD
from src.docs.schemas import CreateDocument


async def download_from_yadisk(ya_disk_url: str, output_file: str = "src/tmp/new_data.csv"):
    """
    Downloads a CSV file from Yandex Disk.

    Args:
        ya_disk_url (str): The public link to the file on Yandex Disk.
        output_file (str): The path where the downloaded CSV file will be saved.

    Returns:
        str: The path to the saved file.

    Raises:
        HTTPException: If there is an error retrieving the download link or downloading the file.
    """
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    try:
        async with AsyncClient() as client:
            final_url = base_url + urlencode(dict(public_key=ya_disk_url))
            response = await client.get(final_url)
            response.raise_for_status()

            download_url = response.json().get('href')
            if not download_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Не удалось получить ссылку на загрузку"
                )

            async with client.stream('GET', download_url, follow_redirects=True) as download_resp:
                download_resp.raise_for_status()
                with open(output_file, mode="wb") as file:
                    async for chunk in download_resp.aiter_bytes():
                        file.write(chunk)

        return output_file

    except HTTPStatusError as http_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTTP ошибка при попытке загрузки файла: {http_err}"
        ) from http_err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Произошла ошибка: {err}"
        ) from err

async def download_file(file: UploadFile, output_file: str = "src/tmp/new_data.csv") -> str:
    """
    Saves an uploaded file from FastAPI.

    Args:
        file (UploadFile): The uploaded file.
        output_file (str): The path where the uploaded file will be saved.

    Returns:
        str: The path to the saved file.
    """
    with open(output_file, "wb") as file_create:
        file_create.write(await file.read())
    return output_file

def get_documents(file_path: str, sep: str) -> List[CreateDocument]:
    """
    Creates a list of documents from a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        sep (str): The delimiter used in the CSV file.

    Returns:
        List[CreateDocument]: A list of CreateDocument objects created from the CSV data.
    """
    df = pd.read_csv(file_path, sep=sep)
    df['created_date'] = pd.to_datetime(df['created_date'])
    df['rubrics'] = df['rubrics'].apply(lambda rubric: json.loads(rubric.replace("'", '"')))

    return [
        CreateDocument(
            rubrics=row['rubrics'],
            text=row['text'],
            created_date=row['created_date']
        ) for _, row in df.iterrows()
    ]

async def import_csv(file_path: str, sep: str, service: DocumentCRUD) -> JSONResponse:
    """
    Imports documents from a CSV file into the database.

    Args:
        file_path (str): The path to the CSV file.
        sep (str): The delimiter used in the CSV file.
        service (DocumentCRUD): The service for managing documents in the database.

    Returns:
        JSONResponse: A response indicating that the documents were successfully added.
    """
    documents_to_add: List[CreateDocument] = get_documents(file_path, sep)
    await service.create_many(documents_to_add)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Documents added successfully"}
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_from_yadisk("https://disk.yandex.ru/d/UYooXd9q2yqTMQ"))
