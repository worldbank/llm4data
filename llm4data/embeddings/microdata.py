from dataclasses import dataclass
from llm4data.embeddings.base import EmbeddingModel


@dataclass
class MicrodataEmbedding(EmbeddingModel):
    data_type: str = "microdata"


microdata_embeddings = MicrodataEmbedding(
    model_name="instruct",
    distance="Cosine",
    embedding_cls="HuggingFaceInstructEmbeddings",
    is_instruct=True,
    embed_instruction="Represent the economic development metadata description for retrieval; Input: ",
    query_instruction="Represent the text for retrieving economic development metadata descriptions; Input: ",
)
