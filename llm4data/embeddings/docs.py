from dataclasses import dataclass
from llm4data.embeddings.base import EmbeddingModel

DOCS_EMBEDDINGS: EmbeddingModel = None


@dataclass
class DocsEmbedding(EmbeddingModel):
    data_type: str = "docs"


def get_docs_embeddings():
    global DOCS_EMBEDDINGS

    if DOCS_EMBEDDINGS is None:
        DOCS_EMBEDDINGS = DocsEmbedding(
            model_name="all-MiniLM-L6-v2",
            distance="Cosine",
            embedding_cls="HuggingFaceEmbeddings",
            is_instruct=False,
        )

    return DOCS_EMBEDDINGS
