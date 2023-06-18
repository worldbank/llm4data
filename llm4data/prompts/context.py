import json
from llm4data.index import get_docs_index, get_indicators_index
from llm4data import configs
from hashlib import md5
from llm4data.schema.schema2info import get_doc_id, get_doc_title, get_doc_authors
from langchain.docstore.document import Document

indicators = get_indicators_index()
docs = get_docs_index()

def get_hash_id(text: str):
    return md5(text.encode("utf-8")).hexdigest()


def get_page(doc: Document, offset=0, default=-1):
    """Get the page number from the document metadata.

    We use offset=1 because the page numbers we want in the metadata
    should start from 1, while the page numbers in the PDF start from 0.
    """

    return doc.metadata.get('page', default) + offset



def get_contexts(prompt: str, k_docs: int = 5, k_indicators: int = 10, doc_id: str = None):
    # Search for documents
    if doc_id is not None:
        docs_result = docs.similarity_search(prompt, k=k_docs, filter={configs.METADATA_KEY: {"document_description": {"title_statement": {"idno": doc_id}}}})
    else:
        docs_result = docs.similarity_search(prompt, k=k_docs)
    indicators_result = indicators.similarity_search(prompt, k=k_indicators)

    doc_context = []
    indicators_context = []

    doc_context_records = []
    indicators_context_records = []

    for doc in docs_result:
        doc_id = get_doc_id(doc.metadata[configs.METADATA_KEY])
        doc_context.append("<h1>Title: " + get_doc_title(doc.metadata[configs.METADATA_KEY]) + "</h1>")

        if doc.metadata[configs.METADATA_KEY].get("authors"):
            doc_context.append("<h1>Author: " + json.dumps(get_doc_authors(doc.metadata[configs.METADATA_KEY])) + "</h1>")

        if doc_id is not None:
            doc_context.append(f"<p>(id: {doc_id}) (page: {get_page(doc, offset=1)}) {doc.page_content}</p>")
        else:
            doc_context.append(f"<p>(id: {doc_id}) {doc.page_content}</p>")

        doc_context_records.append(dict(id=get_hash_id(doc.page_content), doc_id=doc_id, page=get_page(doc, offset=1), content=doc.page_content))

    for indicator in indicators_result:
        indicator_id = indicator.metadata[configs.METADATA_KEY]["series_code"]
        indicators_context.append(f"<p>(id: {indicator_id}) {indicator.metadata[configs.METADATA_KEY]['name']}</p>")
        indicators_context_records.append(dict(id=get_hash_id(indicator.page_content), indicator_id=indicator_id, name=indicator.metadata[configs.METADATA_KEY]['name']))

    doc_context = "<br>".join(doc_context) if doc_context else ""
    indicators_context = "<br>".join(indicators_context) if indicators_context else ""

    return dict(
        docs_result=[i.dict() for i in docs_result],
        indicators_result=[i.dict() for i in indicators_result],
        doc_context=doc_context,
        indicators_context=indicators_context,
        doc_context_records=doc_context_records,
        indicators_context_records=indicators_context_records,
    )
