from pathlib import Path
import json
import tomli

configs = tomli.load((Path(__file__).parent.parent / "config.toml").open("rb"))

__version__ = "0.0.1.dev0"

indicator2name = dict(
    wdi=json.load((Path(__file__).parent / "wdi2name.json").open("r"))
)
