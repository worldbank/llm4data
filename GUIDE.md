# Guide for indexing documents and data

Create the following directory structure:

```
data/sources/<data_type>/<collection>/
    - <extension>/
    - metadata/
```

For example:

```
data/sources/docs/prwp/
    - pdf/
    - metadata/
```

## Content

Each `<extension>` directory contains the files to be indexed in the format specified by the extension. The files in this directory will be passed to the appropriate LangChain loader.

## Metadata

The `metadata` directory contains the metadata for the documents to be indexed. The files in this directory will be passed to the stored data in the index together with the vector for the each chunk of the content.

To maximize the interoperability and reusability of the functionalities in LLM4Data and other related applications built on top of it, we use the [schema guide](https://mah0001.github.io/schema-guide/) to define the metadata for the documents and data.

Using the standardized schema will allow you to easily integrate your own data and documents with applications built on top of LLM4Data such as the Chat4Dev application.

## Indexing

To index the documents and metadata, run the following command:

```bash
python -m llm4data.scripts.indexing.docs.load_docs --path=data/sources/docs/prwp/pdf --strict
```

This will process the documents and store the vectors generated to the configured vector index.
