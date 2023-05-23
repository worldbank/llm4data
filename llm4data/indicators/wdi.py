"""Create an sqlite database from the World Bank WDI database.
"""
import os
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

from tqdm.auto import tqdm

from sqlalchemy import create_engine, text, Column
from sqlalchemy.types import String, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from openai_tools.prompt import PromptZeros
from openai_tools.parser import parse_misparsed

from llm4data import configs

openai_payload = os.getenv(configs["dirs"]["OPENAI_PAYLOAD_DIR"])
if openai_payload is None:
    raise ValueError("`OPENAI_PAYLOAD_DIR` environment variable is not set. Consider adding it to your config.toml file.")

openai_payload = Path(openai_payload)
task_label = configs["task_labels"]["wdi_sql"]

prompt_manager = PromptZeros(
    payloads_dir=openai_payload,
    task_label=task_label,
)

WDI_DB_URL = os.getenv("WDI_DB_URL")

if WDI_DB_URL is None:
    raise ValueError("WDI_DB_URL environment variable is not set. Consider adding it to your config.toml file.")

engine = create_engine(WDI_DB_URL, echo=False)
session = sessionmaker(bind=engine)()
Base = declarative_base()


class WDI(Base):
    __tablename__ = "wdi"

    id = Column(Integer, primary_key=True)
    indicator = Column(String)
    name = Column(String)
    country = Column(String)
    country_id = Column(String)
    country_iso3 = Column(String)
    date = Column(Date)
    value = Column(Float)
    unit = Column(String)
    obs_status = Column(String)
    decimal = Column(Integer)
    year = Column(Integer)

    __llm_fields__ = [
        "indicator",
        # "name",
        "country",
        "country_iso3",
        "year",
        "value"
    ]

    def __repr__(self):
        return f"<WDI(indicator='{self.indicator}', name='{self.name}', country='{self.country}', country_id='{self.country_id}', country_iso3='{self.country_iso3}', date='{self.date}', year='{self.year}', value='{self.value}', unit='{self.unit}', obs_status='{self.obs_status}', decimal='{self.decimal}')>"

    def to_dict(self):
        return {
            "indicator": self.indicator,
            "name": self.name,
            "country": self.country,
            "country_id": self.country_id,
            "country_iso3": self.country_iso3,
            "date": self.date,
            "value": self.value,
            "unit": self.unit,
            "obs_status": self.obs_status,
            "decimal": self.decimal,
            "year": self.year,
        }

    @classmethod
    def from_dict(cls, d):
        d = d.copy()

        # Normalize keys
        if "indicator_id" in d:
            d["indicator"] = d.pop("indicator_id")
        if "indicator_name" in d:
            d["name"] = d.pop("indicator_name")
        if "country_name" in d:
            d["country"] = d.pop("country_name")

        year = int(d["date"])
        date = datetime(year, 1, 1)

        return cls(
            indicator=d["indicator"],
            name=d["name"],
            country=d["country"],
            country_id=d["country_id"],
            country_iso3=d["country_iso3"],
            date=date,
            value=d["value"],
            unit=d["unit"],
            obs_status=d["obs_status"],
            decimal=d["decimal"],
            year=year,
        )

    @classmethod
    def from_json(cls, json_path):
        return cls.from_dict(json.loads(json_path.read_text()))

    @classmethod
    def from_jsons(cls, jsons_dir):
        return [cls.from_json(p) for p in jsons_dir.glob("*.json")]

    @classmethod
    def from_jsons_dir(cls, jsons_dir):
        return [cls.from_json(p) for p in jsons_dir.glob("*.json")]

    @classmethod
    def from_indicator_json(cls, json_path):
        return [cls.from_dict(data) for data in json.loads(json_path.read_text())]

    @classmethod
    def from_indicator_jsons(cls, jsons_dir):
        indicators = []
        for p in jsons_dir.glob("*.json"):
            indicators.extend(cls.from_indicator_json(p))

        return indicators

    @classmethod
    def load_wdi_jsons(cls, wdi_jsons_dir: Path):
        """Load the WDI data stored in JSON
        files and save them to an sqlite database.

        Structure is based on the output of `scripts/scrapers/indicators/wdi.py`.

        Do bulk insert.
        """

        wdi_jsons_dir = Path(wdi_jsons_dir)

        if not wdi_jsons_dir.exists() or not wdi_jsons_dir.is_dir():
            raise ValueError(f"Invalid wdi_jsons_dir: {wdi_jsons_dir}")

        wdi_jsons = list(wdi_jsons_dir.glob("*.json"))
        print(f"Found {len(wdi_jsons)} WDI JSON files.")

        wdi_jsons = sorted(wdi_jsons)
        for wdi_json in tqdm(wdi_jsons):
            wdi_objects = cls.from_indicator_json(wdi_json)
            session.bulk_save_objects(wdi_objects)
            session.commit()

    @classmethod
    def run_sql(cls, sql, params=None, pandas=True, as_dict=False, to_markdown=False, drop_na=True, num_samples=20):
        """Example:
        sql = "SELECT * FROM wdi WHERE indicator = :indicator"
        params = {"indicator": "NY.GDP.PCAP.CD"}

        df = WDI.run_sql(sql, params=params, pandas=True)
        """
        query = text(sql)
        params = params or {}

        data = []

        with engine.connect() as conn:
            results = conn.execute(query, params)

            for record in results:
                d = record._asdict()
                try:
                    d = WDI(**d)
                    data.append(d if not (pandas or as_dict) else d.to_dict())
                except TypeError:
                    data.append(d)

        data_df = pd.DataFrame(data)

        if drop_na:
            data_df = data_df.dropna(axis=1, how="all")

        if "year" in data_df.columns and "country" in data_df.columns:
            sample = data_df.sort_values(["year", "country"], ascending=False).head(num_samples)
        elif "year" in data_df.columns:
            sample = data_df.sort_values(["year"], ascending=False).head(num_samples)
        else:
            sample = data_df.head(num_samples)

        if to_markdown:
            # to_markdown takes the highest precedence
            # data = data.to_markdown(tablefmt="grid")
            data = data.to_markdown()
        elif as_dict:
            data = data_df.replace(np.nan, None).to_dict(orient="records")
        elif pandas:
            # as_dict supercedes pandas flag
            data = data_df
        else:
            raise ValueError("Invalid combination of flags. At least one of pandas, as_dict, to_markdown must be True.")

        return dict(data=data, sample=sample.to_dict(orient="records"))


class WDIIndicator(WDI):
    def __init__(self, indicator_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.indicator_id = indicator_id

    def llm2sql(self, prompt):
        now = datetime.now().date()
        table = self.__tablename__
        fields = ", ".join(self.__llm_fields__)

        template = f"""Current date: {now}

I have a database containing data from the WDI indicators. Write an SQL query for the prompt: ```{{{{user_content}}}}```

table: {table}
fields: {fields}

Only the indicator can parameterized and you must fill the rest. Use the convention :indicator and not `?`. Use country_iso3 when querying, use country in the result.

Use the last 10 years if no year is specified. Drop rows with no value.

Return the entire row if useful for the prompt. If it will help in the analysis and if it makes sense, always add the year in the `SELECT` clause if it is not already there.

Return the output as JSON for json.loads: {{"query_string": <SQL>}}"""

        response = prompt_manager.send_prompt(
            user_content=prompt,
            user_template=template,
            return_data=True,
        )

        try:
            content = parse_misparsed(
                response["content"].strip(),
                open="{",
                close="}",
                normalize_newline=True,
                to_json=True,
            )
            query_string = content["query_string"]
        except json.JSONDecodeError:
            query_string = response["content"].strip()

        return query_string

    def llm2sql_answer(self, prompt, params=None, pandas=True, as_dict=False, to_markdown=False, drop_na=True, num_samples=20):
        sql = self.llm2sql(prompt)

        if params is None:
            params = {}

        params["indicator"] = self.indicator_id

        data = self.run_sql(sql, params=params, pandas=pandas, as_dict=as_dict, to_markdown=to_markdown, drop_na=drop_na, num_samples=num_samples)

        payload = dict(
            sql=sql,
            params=params,
            data=data,
            num_samples=num_samples,
        )

        return payload


Base.metadata.create_all(engine)
