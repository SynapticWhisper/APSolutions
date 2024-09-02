import logging
from typing import Any, AsyncGenerator, List
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_streaming_bulk, async_scan
from src.config import settings
from src.docs.schemas import ESDocumentModel

logging.basicConfig(filename="ElasticLogs.log", level=logging.INFO)

class AsyncESClient:
    INDEX_NAME = "documents"

    def __init__(self):
        self._es_client: AsyncElasticsearch = AsyncElasticsearch(
            cloud_id=settings.es_url,
            api_key=settings.es_api_key
        )
    
    @classmethod
    async def __generate_docs(cls, documents: List[ESDocumentModel]):
        for document in documents:
            yield {
                "_index": cls.INDEX_NAME,
                "_id": document.id,
                "_source": {
                    "text": document.text
                }
            }

    async def add_many(self, document_list: List[ESDocumentModel]) -> list | None:
        errors: list = []
        async for ok, result in async_streaming_bulk(self._es_client, self.__generate_docs(document_list)):
            action, result = result.popitem()
            if not ok:
                logging.info("Failed to %s document %s", action, result)
                errors.append(result)
        return errors if errors else None

    async def add_document(self, document: ESDocumentModel) -> None:
        await self._es_client.index(index=self.INDEX_NAME, id=document.id, document={'text': document.text})

    async def delete_document(self, document_id: int) -> None:
        await self._es_client.delete(index=self.INDEX_NAME, id=document_id)
    
    async def search_documents(self, query: str) -> AsyncGenerator[Any, Any, int]:
        async for doc in async_scan(
            client=self._es_client,
            index=self.INDEX_NAME,
            query={"query": {"match": {"text": query}}}
        ):
            yield doc["_id"]
    
    async def on_startup(self, document_list: List[ESDocumentModel]) -> list | None:
        return await self.add_many(document_list)