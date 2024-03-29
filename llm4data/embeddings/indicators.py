from typing import Optional
from dataclasses import dataclass
from llm4data.embeddings.base import EmbeddingModel

INDICATORS_EMBEDDINGS: Optional[EmbeddingModel] = None


@dataclass
class IndicatorsEmbedding(EmbeddingModel):
    data_type: str = "indicators"


def get_indicators_embeddings():
    global INDICATORS_EMBEDDINGS

    if INDICATORS_EMBEDDINGS is None:
        # INDICATORS_EMBEDDINGS = IndicatorsEmbedding(
        #     model_name="instruct",
        #     distance="Cosine",
        #     embedding_cls="HuggingFaceInstructEmbeddings",
        #     is_instruct=True,
        #     embed_instruction="Represent the Economic Development description for retrieval; Input: ",
        #     query_instruction="Represent the Economic Development prompt for retrieving descriptions; Input: ",
        # )
        INDICATORS_EMBEDDINGS = IndicatorsEmbedding(
            model_name="avsolatorio/GIST-small-Embedding-v0",
            distance="Cosine",
            embedding_cls="HuggingFaceEmbeddings",
            is_instruct=False,
        )

    return INDICATORS_EMBEDDINGS
