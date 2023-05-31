import os
import warnings
from pathlib import Path
from typing import Union, Optional
from dataclasses import dataclass


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
    llm4data_dir: Union[str, Path] = os.getenv("LLM4DATA_DIR", "")
    llm4data_cache_dir: Union[str, Path] = os.getenv("LLM4DATA_CACHE_DIR", "")
    openai_payload_dir: Union[str, Path] = os.getenv("OPENAI_PAYLOAD_DIR", "")

    _exception_template = "`{dirvar}` environment variable is not set. Consider adding it to your .env file."

    def __post_init__(self):
        self.llm4data_dir = self._process_dir(self.llm4data_dir, "LLM4DATA_DIR")
        self.llm4data_cache_dir = self._process_dir(self.llm4data_cache_dir, "LLM4DATA_CACHE_DIR")
        self.openai_payload_dir = self._process_dir(self.openai_payload_dir, "OPENAI_PAYLOAD_DIR")

    def _process_dir(self, dirname: Union[str, Path], dirvar: str) -> Path:
        if not dirname:
            raise ValueError(self._exception_template.format(dirvar=dirvar))

        dirname = Path(dirname)
        if not dirname.exists():
            warnings.warn(f"{dirvar}={dirname} does not exist. Creating it now...")
            dirname.mkdir(parents=True)

        return dirname


@dataclass
class TaskLabelsConfig:
    wdi_sql: str = os.getenv("TASK_LABEL_WDI_SQL", "")

    def __post_init__(self):
        if not self.wdi_sql:
            raise ValueError(
                "`TASK_LABEL_WDI_SQL` environment variable is not set. Consider adding it to your .env file."
            )


@dataclass
class EmbeddingConfig:
    model_size = {
        "all-MiniLM-L6-v2": 384,
        "multi-qa-mpnet-base-dot-v1": 768,
    }

    data_type: str
    model_name: str
    collection_name: str
    distance: str
    size: int
    max_tokens: int
    embedding_cls: str

    is_instruct: bool
    embed_instruction: str
    query_instruction: str

    @property
    def model_id(self):
        return f"{self.data_type}_{self.model_name}_{self.collection_name}_{self.distance}_{self.size}_{self.max_tokens}_{self.is_instruct}"

    def __post_init__(self):
        if self.is_instruct:
            if not (self.embed_instruction and self.query_instruction):
                raise ValueError(
                    "`embed_instruction` and `query_instruction` must be set if `is_instruct` is True."
                )


@dataclass
class DocsEmbeddingConfig(EmbeddingConfig):
    data_type: str = "docs"


@dataclass
class IndicatorsEmbeddingConfig(EmbeddingConfig):
    data_type: str = "indicators"


@dataclass
class MicrodataEmbeddingConfig(EmbeddingConfig):
    data_type: str = "microdata"


# Instantiate the config objects
wdidb = WDIDBConfig()
dirs = DirsConfig()  # NOTE: `dirs` is a reserved keyword in Python
task_labels = TaskLabelsConfig()
