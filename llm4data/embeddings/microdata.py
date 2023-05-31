from langchain.embeddings import HuggingFaceInstructEmbeddings
from qdrant_client.http import models


class MicrodataInstructEmbeddings:
    collection_name = "microdata"
    distance = models.Distance.COSINE
    embeddings = HuggingFaceInstructEmbeddings(
        embed_instruction="Represent the economic development metadata description for retrieval; Input: ",
        query_instruction="Represent the text for retrieving economic development metadata descriptions; Input: ",
    )
    max_tokens = embeddings.client.max_seq_length
    size = 768


microdata_embeddings = MicrodataInstructEmbeddings()
