import os
from typing import Optional, Union
from langchain_community.vectorstores import Qdrant
import qdrant_client
from qdrant_client.http import models

from ..embeddings.docs import get_docs_embeddings
from ..embeddings.indicators import get_indicators_embeddings
from ..embeddings.microdata import get_microdata_embeddings

_CLIENT = None


def collection_exists(collection_name: str) -> bool:
    colls = get_index_client().get_collections()
    return collection_name in [i.name for i in colls.collections]


def get_index_client(path: Optional[str] = None):
    global _CLIENT
    if _CLIENT is None:
        if path is not None:
            _CLIENT = qdrant_client.QdrantClient(path=path, prefer_grpc=True)
        else:
            url = os.environ.get("QDRANT_URL")
            if url is not None:
                port = os.environ.get("QDRANT_PORT")
                if port is not None:
                    url += f":{port}"
                _CLIENT = qdrant_client.QdrantClient(url=url, prefer_grpc=False)
            else:
                path = os.environ.get("QDRANT_PATH")
                if path is not None:
                    _CLIENT = qdrant_client.QdrantClient(path=path, prefer_grpc=True)
                else:
                    raise ValueError("QDRANT_URL or QDRANT_PATH not set in the environment")

    return _CLIENT


def get_index_collection(embeddings, path: Optional[str] = None, recreate: bool = False):
    client = get_index_client(path=path)

    if recreate:
        client.recreate_collection(
            collection_name=embeddings.collection_name,
            vectors_config=models.VectorParams(
                size=embeddings.size, distance=embeddings.distance
            ),
        )

    if not collection_exists(embeddings.collection_name):
        client.create_collection(
            collection_name=embeddings.collection_name,
            vectors_config=models.VectorParams(
                size=embeddings.size, distance=embeddings.distance
            ),
        )

    return Qdrant(
        client=client,
        collection_name=embeddings.collection_name,
        embeddings=embeddings.embeddings,
    )


def get_docs_index(path: Optional[str] = None, recreate: bool = False):
    return get_index_collection(get_docs_embeddings(), path=path, recreate=recreate)


def get_indicators_index(path: Optional[str] = None, recreate: bool = False):
    return get_index_collection(
        get_indicators_embeddings(), path=path, recreate=recreate
    )


def get_microdata_index(path: Optional[str] = None, recreate: bool = False):
    return get_index_collection(
        get_microdata_embeddings(), path=path, recreate=recreate
    )
