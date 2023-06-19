"""Given a dump of the WDI indicators contained in WDIEXCEL.xlsx file,
process them to generate the text for the embedding, extract the metadata
for the payload, and load them into the vector index.
"""
from typing import Union
from pathlib import Path
from tqdm.auto import tqdm
import fire
from .indicators import add_indicators, indicators_index
import json
from metaschema.indicators2 import IndicatorsSchema


def load_indicators(collection_dir: Path):
    """Load the indicators from the collection directory.

    Args:
        collection_dir (Path): Path to the collection directory.
    """
    cname = indicators_index.collection_name

    collection_dir = Path(collection_dir)
    text_dir = collection_dir / "text"
    metadata_dir = collection_dir / "metadata"
    assert text_dir.exists(), f"{text_dir} does not exist."
    assert metadata_dir.exists(), f"{metadata_dir} does not exist."
    assert collection_dir.exists(), f"{collection_dir} does not exist."

    indexed_indicators_path = collection_dir / f"indexed_indicators-{cname}.txt"
    failed_indicators_path = collection_dir / f"failed_indicators-{cname}.txt"

    print("Indexed indicators path:", indexed_indicators_path)

    indexed_indicators = set()
    if indexed_indicators_path.exists():
        print("Loading indexed indicators...")
        with open(indexed_indicators_path, "r") as f:
            for line in f:
                indexed_indicators.add(line.strip())

    print("Indexed indicators:", len(indexed_indicators))


    for indicator_path in tqdm(sorted(text_dir.glob("*.txt"))):
        if str(indicator_path) in indexed_indicators:
            continue
        metadata_path = metadata_dir / f"{indicator_path.stem}.json"

        try:
            metadata = json.loads(metadata_path.read_text())
            text = indicator_path.read_text()

            s = IndicatorsSchema(**metadata)

            add_indicators(
                text=text,
                metadata=s.dict(exclude_none=True),
            )

            with open(indexed_indicators_path, "a+") as f:
                f.write(f"{indicator_path}\n")

        except KeyboardInterrupt:
            raise KeyboardInterrupt

        except Exception as e:
            with open(failed_indicators_path, "a+") as f:
                f.write(f"{indicator_path}\t{e}\n")
            continue


def main(collection_dir: Union[str, Path]):

    collection_dir = Path(collection_dir).expanduser()
    assert collection_dir.exists(), f"File {collection_dir} does not exist."

    print(f"Loading indicators from {collection_dir}...")
    load_indicators(collection_dir)


if __name__ == "__main__":
    # python -m llm4data.scripts.indexing.indicators.load_indicators --collection_dir=data/sources/indicators/wdi
    fire.Fire(main)
