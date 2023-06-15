import json
import requests
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm
import fire
import backoff

from llm4data import indicator2name


class WDIException(BaseException):
    pass


@backoff.on_exception(backoff.expo, WDIException, max_tries=20)
def get_json(url):
    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise WDIException(e)
    except json.decoder.JSONDecodeError as e:
        raise WDIException(e)


class IndicatorScraper:
    def __init__(self, indicator_id, data_dir):
        self.indicator_id = indicator_id
        self.data_dir = Path(data_dir)

    def get_api_url(self, page: int = 1, per_page: int = 1000):
        return f"https://api.worldbank.org/v2/country/all/indicator/{self.indicator_id}?format=json&page={page}&per_page={per_page}"

    def scrape(self):
        page = 1
        _json = get_json(self.get_api_url(page))

        try:
            data = _data = _json[1]
        except IndexError:
            print(f"Skipping (IndexError): {self.indicator_id}")
            return None

        total = _json[0]["pages"]
        # print(f"Total pages: {total}")

        for page in tqdm(
            range(2, total + 1), desc=f"Scraping: ({self.indicator_id})", position=1
        ):
            _data = get_json(self.get_api_url(page))[1]
            data += _data

        data = [self.normalize_record(d) for d in data]

        return data

    @property
    def filename(self):
        return self.data_dir / (self.indicator_id + ".json")

    def save(self, data):
        self.filename.parent.mkdir(exist_ok=True, parents=True)
        self.filename.write_text(json.dumps(data, indent=2))

    def run(self, force: bool = False):
        if not force and self.filename.exists():
            print(f"Skipping: {self.filename}")
            return

        data = self.scrape()

        if data is not None:
            self.save(data)

    def normalize_record(self, data):
        return {
            "indicator_id": data["indicator"]["id"],
            "indicator_name": data["indicator"]["value"],
            "country_id": data["country"]["id"],
            "country_name": data["country"]["value"],
            "country_iso3": data["countryiso3code"],
            "date": data["date"],
            "value": data["value"],
            "unit": data["unit"],
            "obs_status": data["obs_status"],
            "decimal": data["decimal"],
        }


def scrape_indicators(data_dir, force: bool = False):
    indicators = sorted(indicator2name)

    for indicator in tqdm(indicators, desc="Scraping data...", position=0):
        indicator = IndicatorScraper(indicator, data_dir)
        indicator.run(force=force)


if __name__ == "__main__":
    # python -m scripts.scrapers.indicators.wdi --data_dir=data/indicators/wdi --force
    fire.Fire(scrape_indicators)
