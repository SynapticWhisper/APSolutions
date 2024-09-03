import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import pandas as pd
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from httpx import AsyncClient, HTTPStatusError
from typing import List
from urllib.parse import urlencode

from src.docs.service import DocumentCRUD
from src.docs.schemas import CreateDocument


async def download_from_yadisk(ya_disk_url: str, output_file: str = "src/tmp/new_data.csv"):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    try:
        async with AsyncClient() as client:
            final_url = base_url + urlencode(dict(public_key=ya_disk_url))
            response = await client.get(final_url)
            response.raise_for_status()

            download_url = response.json().get('href')
            if not download_url:
                raise HTTPException(status_code=500, detail="Не удалось получить ссылку на загрузку")

            async with client.stream('GET', download_url, follow_redirects=True) as download_response:
                download_response.raise_for_status()
                with open(output_file, mode="wb") as file:
                    async for chunk in download_response.aiter_bytes():
                        file.write(chunk)

        return output_file

    except HTTPStatusError as http_err:
        raise HTTPException(status_code=500, detail=f"HTTP ошибка при попытке загрузки файла: {http_err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка: {err}")
    
async def download_file(file: UploadFile, output_file: str = "src/tmp/new_data.csv") -> str:
    with open(output_file, "wb") as file_create:
        file_create.write(await file.read())
    return output_file


def get_documnets(file_path: str, sep: str) -> List[CreateDocument]:
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
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        documents_to_add: List[CreateDocument] = await loop.run_in_executor(pool, get_documnets, file_path, sep)
    await service.create_many(documents_to_add)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Documents added successfully"})


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_from_yadisk("https://disk.yandex.ru/d/UYooXd9q2yqTMQ"))
