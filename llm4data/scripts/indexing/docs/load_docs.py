from typing import Optional, Union
from pathlib import Path
from tqdm.auto import tqdm
import json
import fire

from .docs import add_pdf_document, docs_index

SUPPORTED_EXTENSIONS = ["pdf"]


def load_doc_to_index(doc_path: Path, metadata: Optional[dict] = None, strict: bool = False):
    assert (
        doc_path.exists() and doc_path.is_file()
    ), f"Invalid document path: {doc_path}"
    assert (
        doc_path.suffix == ".pdf"
    ), f"Invalid document extension: {doc_path.suffix}, expected .pdf"

    if metadata is None:
        # Try to load the metadata from the file
        # following the convention <doc_path>.metadata.json
        # in the same folder.
        metadata_path = doc_path.with_suffix(".metadata.json")

        if not metadata_path.exists():
            # If no metadata is present in the same folder
            # try to load it from the metadata folder.
            metadata_path = doc_path.parent / "metadata" / metadata_path.name

            if not metadata_path.exists():
                # If no metadata is present in the same folder
                # try to load it from the sibling of the parent folder.
                metadata_path = doc_path.parent.parent / "metadata" / metadata_path.name

        if metadata_path.exists():
            metadata = json.load(metadata_path.open())

    if strict:
        assert metadata is not None, f"Metadata not found for {doc_path}"

    add_pdf_document(str(doc_path), metadata)


def load_docs_to_index(docs_dir: Path, strict: bool = False):
    # Load the previously indexed documents.
    cname = docs_index.collection_name
    extension = docs_dir.name

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Invalid extension: {extension}, expected one of {SUPPORTED_EXTENSIONS}"
        )

    indexed_docs_path = docs_dir.parent / f"indexed_docs-{cname}.txt"
    failed_docs_path = docs_dir.parent / f"failed_docs-{cname}.txt"

    print("Indexed docs path:", indexed_docs_path)

    indexed_docs = set()
    if indexed_docs_path.exists():
        print("Loading indexed docs...")
        with open(indexed_docs_path, "r") as f:
            for line in f:
                indexed_docs.add(line.strip())

    print("Indexed docs:", len(indexed_docs))

    doc_paths = sorted(
        docs_dir.glob(f"*.{extension}"),
        reverse=True,
        key=lambda x: int(x.stem.lstrip("D")),
    )

    print("Total docs:", len(doc_paths))

    for doc_path in tqdm(doc_paths):
        if str(doc_path) in indexed_docs:
            continue

        try:
            load_doc_to_index(doc_path, strict=strict)
            # Log documents that were indexed successfully in a file.

            with open(indexed_docs_path, "a+") as f:
                f.write(f"{doc_path}\n")

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            with open(failed_docs_path, "a+") as f:
                # Log the file path and the error message.
                f.write(f"{doc_path}\t{e}\n")

            continue


def main(path: Union[str, Path], strict: bool = False):
    # strict: if True, the script will fail if the document metadata is not found.
    path = Path(path)

    if path.is_file():
        load_doc_to_index(path, strict=strict)
    else:
        load_docs_to_index(path, strict=strict)


if __name__ == "__main__":
    # python -m llm4data.scripts.indexing.docs.load_docs --path=data/sources/docs/prwp/pdf --strict
    fire.Fire(main)
