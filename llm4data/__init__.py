from pathlib import Path
import tomli

configs = tomli.load((Path(__file__).parent.parent / "config.toml").open("rb"))

__version__ = "0.0.1.dev0"
