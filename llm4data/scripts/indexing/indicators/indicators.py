from typing import List, Optional, Union
from langchain.text_splitter import NLTKTextSplitter
from langchain.docstore.document import Document
from llm4data import configs
from llm4data.index import get_indicators_index


# Get access to the Qdrant docs collection
indicators_index = get_indicators_index()
text_splitter = NLTKTextSplitter()


def build_document(text: str, metadata: dict = None):
    # Load the document
    document = Document(page_content=text, metadata={configs.METADATA_KEY: metadata} if metadata else {})

    return document


def add_indicators(text: Union[str, List[str]], metadata: Optional[Union[dict, List[dict]]] = None):
    # Load the document
    if isinstance(text, str):
        documents = [build_document(text, metadata)]
    else:
        documents = [build_document(text, meta) for text, meta in zip(text, metadata)]

    # Add the document to the collection
    indicators_index.add_documents(documents)
