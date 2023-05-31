from langchain.embeddings import HuggingFaceInstructEmbeddings, HuggingFaceEmbeddings
from qdrant_client.http import models


class DocsInstructEmbeddings:
    def __init__(self) -> None:

        self.model_name = "InstructEmbeddings"
        self.collection_name = "docs_instruct"
        self.distance = models.Distance.COSINE
        self.embeddings = HuggingFaceInstructEmbeddings(
            embed_instruction="Represent the passage for retrieval; Input: ",
            query_instruction="Represent the prompt for retrieving the most relevant passage; Input: ",
        )
        self.max_tokens = self.embeddings.client.max_seq_length
        self.size = 768


class DocsHuggingFaceEmbeddings:
    model_size = {
        "instruct": 768,
        "all-MiniLM-L6-v2": 384,
        "multi-qa-mpnet-base-dot-v1": 768,
    }

    def __init__(self, model_name):
        # model_name = "all-MiniLM-L6-v2"
        # model_name = "multi-qa-mpnet-base-dot-v1"
        self.model_name = model_name
        self.collection_name = f"docs_{model_name}"
        self.distance = models.Distance.COSINE
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.size = self.model_size[model_name]
        self.max_tokens = self.embeddings.client.max_seq_length


# docs_embeddings = DocsInstructEmbeddings()
docs_embeddings = DocsHuggingFaceEmbeddings("all-MiniLM-L6-v2")
# docs_embeddings = DocsHuggingFaceEmbeddings("multi-qa-mpnet-base-dot-v1")
