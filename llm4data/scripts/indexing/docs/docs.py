from typing import Optional, Union
from pathlib import Path
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import (
    NLTKTextSplitter,
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

from llm4data.embeddings.docs import get_docs_embeddings
from llm4data import index
from llm4data import configs
from llm4data.schema.schema2info import get_doc_title

# Get the docs embeddings
docs_embeddings = get_docs_embeddings()

# Get access to the Qdrant docs collection
docs_index = index.get_docs_index()

chunk_overlap = 32
chunk_size = docs_embeddings.max_tokens + chunk_overlap

# Create a text splitter
text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    docs_index.embeddings.client.tokenizer,
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
)
# text_splitter = NLTKTextSplitter()


def add_pdf_document(path: Union[str, Path], metadata: Optional[dict] = None):
    # Load the document
    documents = PyMuPDFLoader(str(path)).load_and_split(text_splitter=text_splitter)

    # Add document metadata
    if metadata is not None:
        if len(documents):
            # Index the title of the document
            documents.append(
                Document(page_content=get_doc_title(metadata), metadata=documents[0].metadata)
            )

        for doc in documents:
            doc.metadata[configs.METADATA_KEY] = metadata

    # Add the document to the collection
    # Load the documens in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        docs_index.add_documents(documents[i : i + batch_size])
