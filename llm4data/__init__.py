from pathlib import Path
import json

__version__ = "0.0.1"

indicator2name = dict(
    wdi=json.load((Path(__file__).parent / "wdi2name.json").open("r"))
)
