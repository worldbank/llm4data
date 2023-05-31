"""Base classes for embedding models."""
from typing import Union, Optional
from langchain import embeddings as langchain_embeddings
from pydantic.main import ModelMetaclass
from qdrant_client.http import models
from pydantic.main import ModelMetaclass
from dataclasses import dataclass


# Make the model atomically available
LOADED_MODELS = {}


@dataclass
class EmbeddingModel:
    model_size = {
        "instruct": 768,
        "all-MiniLM-L6-v2": 384,
        "multi-qa-mpnet-base-dot-v1": 768,
    }
    model_name: str
    distance: Union[str, models.Distance]
    embedding_cls: str
    is_instruct: bool
    data_type: str

    collection_name: Optional[str] = None
    size: Optional[int] = None
    max_tokens: Optional[int] = None

    kwargs: Optional[dict] = None
    embed_instruction: Optional[str] = None
    query_instruction: Optional[str] = None

    embeddings: Optional[ModelMetaclass] = None

    @property
    def model_id(self):
        return f"{self.data_type}_{self.model_name}_{self.collection_name}_{self.distance}_{self.size}_{self.max_tokens}_{self.is_instruct}"

    def dict(self):
        return {
            "model_name": self.model_name,
            "distance": self.distance,
            "embedding_cls": self.embedding_cls,
            "is_instruct": self.is_instruct,
            "data_type": self.data_type,
            "collection_name": self.collection_name,
            "size": self.size,
            "max_tokens": self.max_tokens,
            "kwargs": self.kwargs,
            "embed_instruction": self.embed_instruction,
            "query_instruction": self.query_instruction,
        }

    def __post_init__(self):
        self._common_init()
        self._instruct_init()
        self._hf_init()

    def _common_init(self):
        if self.kwargs is None:
            self.kwargs = {}

        if isinstance(self.distance, str):
            self.distance = models.Distance(self.distance)

        if self.size is None:
            if self.model_name not in self.model_size:
                raise ValueError(
                    f"Model size for `{self.model_name}` is not defined. Please add it to the `model_size` dictionary."
                )

            self.size = self.model_size[self.model_name]

        if self.collection_name is None:
            self.collection_name = f"{self.data_type}_{self.model_name}"

    def _instruct_init(self):
        assert isinstance(self.kwargs, dict)

        if self.embedding_cls == "HuggingFaceInstructEmbeddings":
            if not (self.embed_instruction and self.query_instruction):
                raise ValueError(
                    "`embed_instruction` and `query_instruction` must be set if `is_instruct` is True."
                )
            self.kwargs = {
                **self.kwargs,
                "embed_instruction": self.embed_instruction,
                "query_instruction": self.query_instruction
            }

    def _hf_init(self):
        assert isinstance(self.kwargs, dict)

        if self.embedding_cls == "HuggingFaceEmbeddings":
            self.kwargs = {
                **self.kwargs,
                "model_name": self.model_name,
            }


@dataclass
class DocsEmbedding(EmbeddingModel):
    data_type: str = "docs"


@dataclass
class IndicatorsEmbedding(EmbeddingModel):
    data_type: str = "indicators"


@dataclass
class MicrodataEmbedding(EmbeddingModel):
    data_type: str = "microdata"


class EmbeddingModelFactory:
    def get_embedding_model(self, config: EmbeddingModel) -> EmbeddingModel:
        model_id = config.model_id
        print("model_id", model_id)

        if model_id in LOADED_MODELS:
            model = LOADED_MODELS[model_id]
        else:
            model = self._create_model(config)
            LOADED_MODELS[model_id] = model

        return model

    def _create_model(self, config: EmbeddingModel) -> EmbeddingModel:
        return config.__class__(
            **config.dict(),
            embeddings=self._create_embeddings(config),
        )

    def _create_embeddings(self, config: EmbeddingModel) -> ModelMetaclass:
        embdedding = getattr(langchain_embeddings, config.embedding_cls)

        if not isinstance(config.kwargs, dict):
            raise ValueError("`config.kwargs` must be a dict")

        return embdedding(**config.kwargs)
