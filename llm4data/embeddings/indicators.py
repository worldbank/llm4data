from langchain.embeddings import HuggingFaceInstructEmbeddings
from qdrant_client.http import models


class IndicatorsInstructEmbeddings:
    collection_name = "indicators"
    distance = models.Distance.COSINE
    embeddings = HuggingFaceInstructEmbeddings(
        embed_instruction="Represent the Economic Development description for retrieval; Input: ",
        query_instruction="Represent the Economic Development prompt for retrieving descriptions; Input: ",
    )
    max_tokens = embeddings.client.max_seq_length
    size = 768


indicators_embeddings = IndicatorsInstructEmbeddings()
