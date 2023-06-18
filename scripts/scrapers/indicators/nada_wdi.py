from typing import Union
import json
import requests
from pathlib import Path
import fire
from tqdm.auto import tqdm

from metaschema.indicators2 import IndicatorsSchema


def main(nada_headers: Union[str, Path], metadata_dir: Union[str, Path], max_id: int = 2000):
    """
    Args:
        nada_headers: Path to the NADA headers file in JSON format. You can get this from the Network tab in your browser.
        metadata_dir: Path to the directory where the metadata files will be saved.
    """
    nada_headers = Path(nada_headers)
    assert nada_headers.exists(), f"{nada_headers} does not exist"

    metadata_dir = Path(metadata_dir)
    assert metadata_dir.exists(), f"{metadata_dir} does not exist"

    url = lambda no: f"https://dev.ihsn.org/wdi/index.php/metadata/export/{no}/json"
    headers = json.loads(nada_headers.read_text())

    for no in tqdm(range(1, max_id + 1), desc="Scraping", position=1):

        r = requests.get(url(no), headers=headers)
        if r.status_code == 200:
            data = r.json()
            if not data:
                break

            data = IndicatorsSchema(**data)

            filename = metadata_dir / f"{data.series_description.idno}.json"
            filename.write_text(json.dumps(data.dict(exclude_none=True), default=str))
        else:
            break


if __name__ == "__main__":
    # python -m scripts.scrapers.indicators.nada_wdi --nada_headers=secrets/nada_headers.json --metadata_dir=data/sources/indicators/wdi/metadata
    fire.Fire(main)
