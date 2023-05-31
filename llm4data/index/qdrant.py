import os
from langchain.vectorstores import Qdrant
import qdrant_client
from qdrant_client.http import models

from ..embeddings.docs import docs_embeddings
from ..embeddings.indicators import indicators_embeddings
from ..embeddings.microdata import microdata_embeddings

_CLIENT = None


def collection_exists(collection_name: str) -> bool:
    colls = get_qdrant_client().get_collections()
    return collection_name in [i.name for i in colls.collections]


def get_qdrant_client(path: str = None):
    global _CLIENT
    if _CLIENT is None:
        if os.environ.get("QDRANT_URL") is not None:
            url = os.environ.get("QDRANT_URL")
            if os.environ.get("QDRANT_PORT") is not None:
                url += f":{os.environ.get('QDRANT_PORT')}"
            _CLIENT = qdrant_client.QdrantClient(url=url, prefer_grpc=False)
        elif os.environ.get("QDRANT_PATH") is not None:
            path = os.environ.get("QDRANT_PATH")
            _CLIENT = qdrant_client.QdrantClient(path=path, prefer_grpc=True)
        else:
            raise ValueError("QDRANT_URL or QDRANT_PATH not set in the environment")

    return _CLIENT


def get_qdrant_collection(embeddings, path: str = None, recreate: bool = False):
    client = get_qdrant_client(path=path)

    if recreate:
        client.recreate_collection(
            collection_name=embeddings.collection_name,
            vectors_config=models.VectorParams(size=embeddings.size, distance=embeddings.distance),
        )

    if not collection_exists(embeddings.collection_name):
        client.create_collection(
            collection_name=embeddings.collection_name,
            vectors_config=models.VectorParams(size=embeddings.size, distance=embeddings.distance),
        )

    return Qdrant(
        client=client, collection_name=embeddings.collection_name,
        embeddings=embeddings.embeddings
    )


def get_qdrant_docs(path: str = None, recreate: bool = False):
    return get_qdrant_collection(docs_embeddings, path=path, recreate=recreate)


def get_qdrant_indicators(path: str = None, recreate: bool = False):
    return get_qdrant_collection(indicators_embeddings, path=path, recreate=recreate)

def get_qdrant_microdata(path: str = None, recreate: bool = False):
    return get_qdrant_collection(microdata_embeddings, path=path, recreate=recreate)