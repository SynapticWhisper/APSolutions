from fastapi import FastAPI
from src.docs.router import router as DocumnetRouter
# from elasticsearch import AsyncElasticsearch
# from src.database import get_async_session
# from src.docs.es_service import AsyncESClient

app = FastAPI()
# es = AsyncElasticsearch()

# @app.on_event("shutdown")
# async def app_shutdown():
#     await es.close()


app.include_router(DocumnetRouter)