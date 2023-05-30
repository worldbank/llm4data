"""Create an sqlite database from the World Bank WDI data.
"""
from llm4data.llm.indicators.wdi_sql import WDISQL
import fire


def main(wdi_jsons_dir: str):
    WDISQL.load_wdi_jsons(wdi_jsons_dir)


if __name__ == "__main__":
    # python -m scripts.scrapers.indicators.wdi_db  --wdi_jsons_dir=data/indicators/wdi
    fire.Fire(main)
