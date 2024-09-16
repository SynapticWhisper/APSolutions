"""
This module provides an asynchronous client for interacting with an Elasticsearch cluster.

The `AsyncESClient` class includes methods for adding, deleting, and searching documents in an 
Elasticsearch index. It supports both individual document operations and bulk operations, leveraging 
the capabilities of the `AsyncElasticsearch` client and helper functions from the `elasticsearch`
library.

Key functionalities include:
- Bulk addition of documents to the Elasticsearch index.
- Single document addition and deletion by ID.
- Asynchronous search of documents by a text query.
- Graceful shutdown of the Elasticsearch client connection.

Logging is configured to capture information about failed operations, aiding in debugging and
monitoring.
"""

import logging
from typing import Any, AsyncGenerator, List
from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_streaming_bulk, async_scan
from fastapi import HTTPException
from src.config import settings
from src.docs.schemas import ESDocumentModel

logging.basicConfig(filename="ElasticLogs.log", level=logging.INFO)

class AsyncESClient:
    """
    An asynchronous client for interacting with an Elasticsearch cluster.

    Attributes:
        INDEX_NAME (str): The name of the Elasticsearch index used to store documents.
    """
    INDEX_NAME = "documents"

    def __init__(self):
        self._es_client: AsyncElasticsearch = AsyncElasticsearch(settings.es_url)

    @classmethod
    async def __generate_docs(cls, documents: List[ESDocumentModel]):
        """
        A generator that yields documents in a format suitable for bulk indexing in Elasticsearch.

        Args:
            documents (List[ESDocumentModel]): A list of documents to be indexed.

        Yields:
            dict: A dictionary representing the document to be indexed.
        """
        for document in documents:
            yield {
                "_index": cls.INDEX_NAME,
                "_id": document.id,
                "_source": {
                    "text": document.text
                }
            }

    async def add_many(self, document_list: List[ESDocumentModel]) -> int:
        """
        Adds multiple documents to the Elasticsearch index.

        Args:
            document_list (List[ESDocumentModel]): A list of documents to be added.

        Returns:
            Optional[list]: A list of errors if any documents failed, otherwise None.
        """
        errors: int = 0
        async for ok, result in async_streaming_bulk(
            self._es_client,
            self.__generate_docs(document_list)
        ):
            action, result = result.popitem()
            if not ok:
                logging.info("Failed to %s document %s", action, result)
                errors += 1
        return errors

    async def add_document(self, document: ESDocumentModel) -> None:
        """
        Adds a single document to the Elasticsearch index.

        Args:
            document (ESDocumentModel): The document to be added.
        """
        await self._es_client.index(
            index=self.INDEX_NAME,
            id=document.id,
            document={'text': document.text}
        )

    async def delete_document(self, document_id: int) -> None:
        """
        Deletes a document from the Elasticsearch index by its ID.

        Args:
            document_id (int): The ID of the document to be deleted.
        """
        await self._es_client.delete(index=self.INDEX_NAME, id=document_id)

    async def search_documents(self, query: str, limit: int = 20) -> AsyncGenerator[Any, int]:
        """
        Searches for documents in the Elasticsearch index that match the given query.

        Args:
            query (str): The search query string.
            limit (int): The maximum number of documents to return.

        Yields:
            AsyncGenerator[int, None]: An async generator yielding the IDs of matching documents.
        """
        try:
            async for doc in async_scan(
                client=self._es_client,
                index=self.INDEX_NAME,
                query={
                    "query": {
                        "match": {"text": query}
                    },
                    "size": limit,
                }
            ):
                yield int(doc["_id"])
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail="No documents in Elastic index yet") from e

    # async def on_startup(self, document_list: List[ESDocumentModel]) -> list | None:
    #     return await self.add_many(document_list)

    async def on_shutdown(self):
        """
        Closes the connection to the Elasticsearch cluster gracefully.
        """
        await self._es_client.close()
