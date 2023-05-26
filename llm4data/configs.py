import os
from pathlib import Path
from typing import Union
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()


# Define a data class for the database config
@dataclass
class WDIDBConfig:
    table_name: str = os.getenv("WDI_DB_TABLE_NAME")
    engine: str = os.getenv("WDI_DB_ENGINE")
    host: str = os.getenv("WDI_DB_HOST")
    port: int = int(os.getenv("WDI_DB_PORT")) if os.getenv("WDI_DB_PORT") else None
    username: str = os.getenv("WDI_DB_USERNAME")
    password: str = os.getenv("WDI_DB_PASSWORD")

    @property
    def url(self):
        url = f"{self.engine}://{self.username}"

        if self.password:
            url += f":{self.password}"

        if self.host:
            url += f"@{self.host}"

        if self.port:
            url += f":{self.port}"

        return url


@dataclass
class DirsConfig:
    openai_payload_dir: Union[str, Path] = os.getenv("OPENAI_PAYLOAD_DIR")

    def __post_init__(self):
        if self.openai_payload_dir is None:
            raise ValueError("`OPENAI_PAYLOAD_DIR` environment variable is not set. Consider adding it to your .env file.")

        self.openai_payload_dir = Path(self.openai_payload_dir)


@dataclass
class TaskLabelsConfig:
    wdi_sql: str = os.getenv("TASK_LABEL_WDI_SQL")


# Instantiate the config objects
wdidb = WDIDBConfig()
dirs = DirsConfig()  # NOTE: `dirs` is a reserved keyword in Python
task_labels = TaskLabelsConfig()
