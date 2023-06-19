from llm4data.index import get_docs_index
from llm4data import configs
import fire


def create_doc_index(field_name: str, field_schema: str):
    """
    Create a field index for the docs collection.

    Args:
        field_name (str): The name of the field to index.
        field_schema (str): The schema of the field to index.

    Returns:
        dict: The response from the Qdrant server.

    Examples:
        >>> from llm4data.scripts.indexing.create_field_index import create_doc_index
        >>> from llm4data import configs
        >>> create_doc_index("document_description.title_statement.idno", "keyword")
    """

    # Check that the field name starts with "document_description." since that is the
    # expected metadata key for the docs schema.
    assert field_name.startswith("document_description."), f"Field name must start with 'document_description.' but got {field_name}"
    doc_index = get_docs_index()

    indexed = doc_index.client.create_payload_index(
        doc_index.collection_name,
        field_name=f"metadata.{configs.METADATA_KEY}.{field_name}",
        field_schema=field_schema,
    )

    return indexed


def main(data_type: str, field_name: str, field_schema: str):
    if data_type == "docs":
        create_doc_index(field_name, field_schema)
    else:
        raise ValueError(f"Unknown data type {data_type}")


if __name__ == "__main__":
    # python -m llm4data.scripts.indexing.create_field_index --data_type=docs --field_name="document_description.title_statement.idno" --field_schema=keyword
    fire.Fire(main)
