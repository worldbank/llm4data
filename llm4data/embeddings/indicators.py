from dataclasses import dataclass
from llm4data.embeddings.base import EmbeddingModel


@dataclass
class IndicatorsEmbedding(EmbeddingModel):
    data_type: str = "indicators"


indicators_embeddings = IndicatorsEmbedding(
    model_name="instruct",
    distance="Cosine",
    embedding_cls="HuggingFaceInstructEmbeddings",
    is_instruct=True,
    embed_instruction="Represent the Economic Development description for retrieval; Input: ",
    query_instruction="Represent the Economic Development prompt for retrieving descriptions; Input: ",
)
