"""
This module implements the automated theme generation from microdata data dictionary using LLMs.
"""
import json
import numpy as np

from typing import Any, Union
from pathlib import Path

from InstructorEmbedding import INSTRUCTOR
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import TruncatedSVD

from llm_space.utils import get_tiktoken_model

from llm4data.utils.microdata.scraper import fetch_variables
from llm4data.utils.microdata.paths import get_idno_fpath
from llm4data.utils.microdata.helpers import get_label_names
from llm4data.utils.system.cache import memory


embedding_model = INSTRUCTOR("hkunlp/instructor-large")
INSTRUCTION = "Represent the survey variable label for clustering; Input: "
TOKEN_LIMIT = 500
SPECIAL_SEP = "!!!!!"



@memory.cache
def embed_labels(labels):
    prompt_labels = [[INSTRUCTION, label] for label in labels]
    embeddings = embedding_model.encode(prompt_labels)
    return embeddings


def store_variables(idno: str, variables: dict, vars_dir: Union[str, Path] = None) -> None:
    """
    Store the variables locally in data/microdata/variables/<idno>/<idno>_variables.json
    """
    variables_path = get_idno_fpath(idno, vars_dir)
    variables_path.write_text(json.dumps(variables, indent=2))


class ThemeLLM(object):
    """
    ThemeLLM encapsulates the methods for generating themes from microdata data dictionaries using LLMs.

    The class expects a data dictionary as input. The data dictionary can be provided in two ways:
    - a data dictionary in the form of a JSON file
    - an idno of a study in the form of a string. The data dictionary will be retrieved from a specified NADA catalog.
    """

    def __init__(self, idno: str, llm_model_id: str = "gpt-3.5-turbo", data_dictionary: Union[str, Path, dict] = None, catalog_url: str = None, vars_dir: Union[str, Path] = None, desc_dir: Union[str, Path] = None, force: bool = False, persist: bool = True):
        """
        Initialize the ThemeLLM object.

        Args:

            idno: The idno of the study.

            data_dictionary: The data dictionary. It can be provided in two ways:
                - a data dictionary in the form of a JSON file
                - an idno of a study in the form of a string. The data dictionary will be retrieved from a specified NADA catalog.

                NOTE: If this value is not `None`, it will replace the locally stored version of the data_dictionary.

            catalog_url: The URL of the NADA catalog from which the data dictionary will be retrieved.

            vars_dir: The path to the directory where the variables are stored. If the directory does not exist, it is created.
                If vars_dir is None, the default directory is used.

            desc_dir: The path to the directory where the descriptions are stored. If the directory does not exist, it is created.
                If desc_dir is None, the default directory is used.

            force: If True, the data dictionary will be downloaded even if it already exists.

            persist: If True, the data dictionary will be saved to disk.
        """
        self.idno = idno
        self.data_dictionary = data_dictionary
        self.catalog_url = catalog_url

        # Set the variables and descriptions directories.
        self.vars_dir = vars_dir
        self.desc_dir = desc_dir

        # Set the paths to the variables and descriptions.
        self.variables_path = get_idno_fpath(idno=self.idno, vars_dir=self.vars_dir)
        self.clusters_path = self.variables_path.parent / f"{self.idno}_cluster.json"

        # Set the LLM model id.
        self.llm_model_id = llm_model_id

        self._load_data_dictionary(force=force, persist=persist)

    def clean(self):
        """
        Removes the data artifacts associated with the idno.
        """
        if self.variables_path.exists():
            self.variables_path.unlink()

        if self.clusters_path.exists():
            self.clusters_path.unlink()

    def _load_data_dictionary(self, force: bool = False, persist: bool = True):
        """
        Load the data dictionary. First, check if the data dictionary is already loaded. If not, check if it is already downloaded.
        """
        if isinstance(self.data_dictionary, dict):
            # The data dictionary is already loaded.
            if persist: store_variables(self.idno, self.data_dictionary, vars_dir=self.vars_dir)
            return

        if self.data_dictionary is None:
            # Check first if there is a local version?
            if self.variables_path.exists() and not force:
                self.data_dictionary = json.load(open(self.variables_path, "r"))
                return
            else:
                # The data dictionary is not provided. Load it from the catalog.
                self.data_dictionary = fetch_variables(idno=self.idno, catalog_url=self.catalog_url)

        elif isinstance(self.data_dictionary, (str, Path)):
            # The data dictionary is provided as a path to a JSON file.
            self.data_dictionary = json.load(open(self.data_dictionary, "r"))

        else:
            raise ValueError("The data dictionary must be provided as a path to a JSON file or as a dict.")

        if persist: store_variables(self.idno, self.data_dictionary, vars_dir=self.vars_dir)

    def semantic_enrichment(self, max_clusters: int = 20):
        label_names = get_label_names(idno=self.idno, vars_dir=self.vars_dir)

        # Only apply clustering strategy if the number of labels is large.
        # We need to quantify what large means. A possible strategy is to
        # count the number of tokens for the entire set of labels. We then
        # apply the clustering strategy if the number of tokens is greater
        # than 500. We then compute the required number of clusters by dividing
        # the number of tokens by 500.

        # Load the tokenizer for the model.
        encoder = get_tiktoken_model(self.llm_model_id)
        tokens = encoder.encode(SPECIAL_SEP.join(label_names.keys()))

        len_tokens = len(tokens)

        if len_tokens <= TOKEN_LIMIT:
            return {"idno": self.idno, "cluster": {"0": label_names}}

        # We need to cluster the labels.
        n_clusters = min(max_clusters, len_tokens // TOKEN_LIMIT)

        embeddings = self.semantic_embedding(label_names)

        # Apply clustering.
        clusters = self.clustering(embeddings, n_clusters=n_clusters)

        # Group the labels by cluster.
        cluster_labels = {}
        for label, cluster in zip(sorted(label_names.keys()), clusters):
            cluster = str(cluster)

            if cluster not in cluster_labels:
                cluster_labels[cluster] = {}

            cluster_labels[cluster][label] = label_names[label]

        cluster = {"idno": self.idno, "cluster": cluster_labels}

        # Save the cluster to disk.
        self.clusters_path.write_text(json.dumps(cluster, indent=2))

        return cluster

    def semantic_embedding(self, label_names: dict[str, list]):
        # Generate the embeddings for the labels.
        # prompt_labels = [[INSTRUCTION, label] for label in sorted(label_names.keys())]
        # embeddings = embedding_model.encode(prompt_labels)
        labels = sorted(label_names.keys())
        embeddings = embed_labels(labels)

        return np.vstack(embeddings)

    def clustering(self, embeddings: np.ndarray, n_clusters: int = 20, n_components: int = 50, random_state: int = 1029, metric: str = "euclidean", linkage: str = "ward"):
        # Cluster the embeddings on a dimensionality-reduced space.

        aggcl = AgglomerativeClustering(n_clusters=n_clusters, metric=metric, linkage=linkage)
        tsvd = TruncatedSVD(n_components=n_components, random_state=random_state)

        return aggcl.fit_predict(tsvd.fit_transform(embeddings))

    def __str__(self):
        return "ThemeLLM(idno='{}')".format(self.idno)
