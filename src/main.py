from fastapi import FastAPI

from src.docs.router import router as DocumnetRouter
from src.ingestion.router import router as IngestionRouter

# from elasticsearch import AsyncElasticsearch
# from src.database import get_async_session
# from src.docs.es_service import AsyncESClient
# es = AsyncElasticsearch()

# @app.on_event("shutdown")
# async def app_shutdown():
#     await es.close()

app = FastAPI(
    title="Тестовое задание Python",
    description="Простой поисковик по текстам документов. Данные хранятся в БД (PostgreSQL), поисковый индекс в ElasticSearch."
)

app.include_router(DocumnetRouter)
app.include_router(IngestionRouter)

