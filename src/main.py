from fastapi import FastAPI, Depends

from src.docs.router import router as DocumnetRouter
from src.docs.es_service import AsyncESClient
from src.ingestion.router import router as IngestionRouter

app = FastAPI(
    title="Тестовое задание Python",
    description="Простой поисковик по текстам документов. Данные хранятся в БД" \
        "(PostgreSQL), поисковый индекс в ElasticSearch."
)

app.include_router(DocumnetRouter)
app.include_router(IngestionRouter)


@app.on_event("shutdown")
async def app_shutdown(es_service: AsyncESClient = Depends()):
    await es_service.on_shutdown()
