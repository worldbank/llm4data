import json
from pathlib import Path
from typing import Union, Optional
from tqdm.auto import tqdm

import fire
from metaschema.indicators2 import IndicatorsSchema, SeriesDescription


def create_wdi_text(series_description: SeriesDescription):
    """Create the text for the WDI indicator.

    Args:
        series_description: The series description object.
    """

    sd = series_description
    texts = []

    # Text sources

    name = sd.name
    definition = sd.definition_long or sd.definition_short or ""
    dev_relevance = sd.relevance or ""
    stat_concept = sd.statistical_concept or ""

    if name:
        texts.append(f"Indicator name: {name}")
    if definition:
        texts.append(f"Definition: {definition}")
    if dev_relevance:
        texts.append(f"Development relevance: {dev_relevance}")
    if stat_concept:
        texts.append(f"Statistical concept and methodology: {stat_concept}")

    # Text
    text = "\n\n".join(texts)
    text = text.strip()

    return text


def main(metadata_dir: Union[str, Path]):
    metadata_dir = Path(metadata_dir)
    assert metadata_dir.exists(), f"{metadata_dir} does not exist"

    for p in tqdm(sorted(metadata_dir.glob("*.json"))):
        fname = p.parent.parent / "text" / f"{p.stem}.txt"
        if fname.exists():
            continue

        metadata = json.loads(p.read_text())
        s = IndicatorsSchema(**metadata)
        text = create_wdi_text(s.series_description)
        fname.write_text(text)


if __name__ == "__main__":
    # python -m llm4data.schema.indicators.create_wdi_text --metadata_dir=data/sources/indicators/wdi/metadata
    fire.Fire(main)
