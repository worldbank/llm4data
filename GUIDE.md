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


data/sources/indicators/wdi/
    - text/
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


## The World Bank Documents and Reports

The World Bank provides programatic access to open access documents and reports via an API. To index data from the documents and reports, we have to first download the metadata available in the API. Then, we can use the `pdfurl` value in the metadata to scrape the PDFs.

The metadata from the documents and reports API is not using the metadata standard adopted in this library. However, we have implemented a script to easily migrate the metadata from the documents and reports into the metadata standard the library supports. We show below the steps you can take for this migration.

1. Download the metadata and store them in a directory, e.g., `raw_metadata/`. We follow the convention naming the metadata file as `<id>.metadata.json`.
2. Create the source directory for this data, for example, `data/sources/docs/prwp`.
3. Use the `pdfurl` to scrape the PDFs.
4. Store the PDFs in the `pdf` directory under `data/sources/docs/prwp`.
5. Run the following command to migrate the metadata to the standard adopted in this library:

    ```bash
    python -m llm4data.schema.docs.migrate_wbdocs_metadata --source_dir=raw_metadata/ --source_dir=data/sources/docs/prwp/metadata
    ```

6. Run the following command to index the documents:

    ```bash
    python -m llm4data.scripts.indexing.docs.load_docs --path=data/sources/docs/prwp/pdf --strict
    ```

## The World Bank World Development Indicators

The World Bank provides programatic access to the World Development Indicators via an API. To index data from the World Development Indicators, we have to first download the metadata.

We use the NADA Dev catalog to download the metadata because it contains metadata for the WDIs that is already in the metadata standard adopted in this library. We have implemented a script to easily download the metadata from the NADA Dev catalog. We show below the steps you can take to download the metadata and index the data.


```bash
python -m scripts.scrapers.indicators.nada_wdi --nada_headers=secrets/nada_headers.json --metadata_dir=data/sources/indicators/wdi/metadata
```

You will need to create the `secrets/nada_headers.json` file. You can get this from the NADA Dev website. You will need to login to the website and then copy the headers from the browser.

```{warning}
The `secrets` directory is not tracked by git.
```

Once you have downloaded the metadata, you need to create the `text` directory under `data/sources/indicators/wdi`. This directory will contain the text files for each indicator. We will extract relevant information from the metadata and store it in the text files.

    ```bash
    python -m llm4data.schema.indicators.create_wdi_text --metadata_dir=data/sources/indicators/wdi/metadata
    ```

Note that the text is taken from the following fields in the metadata:

    - name
    - definition_long or definition_short
    - relevance
    - statistical_concept
