"""Create an sqlite database from the World Bank WDI database.
"""
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

from tqdm.auto import tqdm

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from openai_tools.parser import parse_misparsed

from llm4data import configs

from llm4data.sources.indicators.wdi import Base, WDI
from llm4data.prompts.indicators.wdi import WDISQLPrompt


engine = create_engine(configs.wdidb.url, echo=False)
session = sessionmaker(bind=engine)()


class WDISQL(WDI):
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
    def run_sql(
        cls,
        sql,
        params=None,
        pandas=True,
        as_dict=False,
        to_markdown=False,
        drop_na=True,
        num_samples=20,
    ):
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
            sample = data_df.sort_values(["year", "country"], ascending=False).head(
                num_samples
            )
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
            raise ValueError(
                "Invalid combination of flags. At least one of pandas, as_dict, to_markdown must be True."
            )

        return dict(data=data, sample=sample.to_dict(orient="records"))

    def llm2sql(self, prompt):
        table = self.__tablename__
        fields = ", ".join(self.__llm_fields__)

        response = WDISQLPrompt().send_prompt(
            prompt=prompt,
            table=table,
            fields=fields,
            send_prompt_kwargs=dict(
                return_data=True,
            ),
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

    def llm2sql_answer(
        self,
        prompt,
        params=None,
        pandas=True,
        as_dict=False,
        to_markdown=False,
        drop_na=True,
        num_samples=20,
    ):
        sql = self.llm2sql(prompt)

        if params is None:
            params = {}

        data = self.run_sql(
            sql,
            params=params,
            pandas=pandas,
            as_dict=as_dict,
            to_markdown=to_markdown,
            drop_na=drop_na,
            num_samples=num_samples,
        )

        payload = dict(
            sql=sql,
            params=params,
            data=data,
            num_samples=num_samples,
        )

        return payload


class WDIIndicatorSQL(WDISQL):
    def __init__(self, indicator_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.indicator_id = indicator_id

    def llm2sql_answer(
        self,
        prompt,
        params=None,
        pandas=True,
        as_dict=False,
        to_markdown=False,
        drop_na=True,
        num_samples=20,
    ):

        if params is None:
            params = {}

        params["indicator"] = self.indicator_id

        return super().llm2sql_answer(
            prompt,
            params=params,
            pandas=pandas,
            as_dict=as_dict,
            to_markdown=to_markdown,
            drop_na=drop_na,
            num_samples=num_samples,
        )


Base.metadata.create_all(engine)
