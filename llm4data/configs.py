import os
from pathlib import Path
from typing import Union, Optional
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()


# Define a data class for the database config
@dataclass
class WDIDBConfig:
    table_name: Optional[str] = os.getenv("WDI_DB_TABLE_NAME")
    engine: Optional[str] = os.getenv("WDI_DB_ENGINE")
    host: Optional[str] = os.getenv("WDI_DB_HOST")
    port: Optional[str] = os.getenv("WDI_DB_PORT")
    username: Optional[str] = os.getenv("WDI_DB_USERNAME")
    password: Optional[str] = os.getenv("WDI_DB_PASSWORD")

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
    openai_payload_dir: Union[str, Path] = os.getenv("OPENAI_PAYLOAD_DIR", "")

    def __post_init__(self):
        if not self.openai_payload_dir:
            raise ValueError(
                "`OPENAI_PAYLOAD_DIR` environment variable is not set. Consider adding it to your .env file."
            )

        self.openai_payload_dir = Path(self.openai_payload_dir)


@dataclass
class TaskLabelsConfig:
    wdi_sql: str = os.getenv("TASK_LABEL_WDI_SQL", "")

    def __post_init__(self):
        if not self.wdi_sql:
            raise ValueError(
                "`TASK_LABEL_WDI_SQL` environment variable is not set. Consider adding it to your .env file."
            )


# Instantiate the config objects
wdidb = WDIDBConfig()
dirs = DirsConfig()  # NOTE: `dirs` is a reserved keyword in Python
task_labels = TaskLabelsConfig()
