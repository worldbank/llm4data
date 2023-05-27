"""Create an sqlite database from the World Bank WDI database.
"""
import json
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.types import String, Integer, Float, Date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


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
        "value",
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
