import os
import asyncio
from urllib.parse import urlencode
from fastapi import HTTPException
from httpx import AsyncClient, HTTPStatusError


async def download_from_yadisk(ya_disk_url: str, output_file: str = "src/files/test_data.csv"):
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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_from_yadisk("https://disk.yandex.ru/d/UYooXd9q2yqTMQ"))
