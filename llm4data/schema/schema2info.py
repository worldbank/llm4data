"""This module contains functions to extract information from the schema."""



def get_doc_id(metadata: dict) -> str:
    """Get the id of the document from the metadata document_description."""
    return metadata["document_description"]["title_statement"]["idno"]


def get_doc_title(metadata: dict) -> str:
    """Get the title of the document from the metadata document_description."""
    return metadata["document_description"]["title_statement"]["title"]


def get_doc_authors(metadata: dict) -> list:
    """Get the authors of the document from the metadata document_description."""
    authors = metadata["document_description"]["authors"]
    full_names = []

    for author in authors:
        full_name = ""
        if author.get("first_name"):
            full_name += author["first_name"]
        if author.get("middle_name"):
            full_name += " " + author["middle_name"]
        if author.get("last_name"):
            full_name += " " + author["last_name"]

        if not full_name.strip():
            full_name = author.get("full_name", "")

        full_names.append(full_name)

    return full_names
