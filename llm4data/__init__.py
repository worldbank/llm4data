import json
import dotenv

from pathlib import Path

# Load environment variables from the .env file.
# Do this before importing any other modules.
dotenv.load_dotenv()

__version__ = "0.0.2"

indicator2name = dict(
    wdi=json.load((Path(__file__).parent / "wdi2name.json").open("r"))
)
