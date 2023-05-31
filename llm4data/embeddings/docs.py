from dataclasses import dataclass
from llm4data.embeddings.base import EmbeddingModel


@dataclass
class DocsEmbedding(EmbeddingModel):
    data_type: str = "docs"


docs_embeddings = DocsEmbedding(
    model_name="all-MiniLM-L6-v2",
    distance="Cosine",
    embedding_cls="HuggingFaceEmbeddings",
    is_instruct=False,
)
