"""
This module implements the automated theme generation from microdata data dictionary using LLMs.
"""
import json
from typing import Any, Union
from pathlib import Path

from InstructorEmbedding import INSTRUCTOR

from llm4data.utils.microdata.scraper import fetch_variables
from llm4data.utils.microdata.paths import get_idno_fpath
from llm4data.utils.microdata.helpers import get_label_names
from llm4data.utils.system.cache import memory


embedding_model = INSTRUCTOR("hkunlp/instructor-large")
INSTRUCTION = "Represent the survey variable label for clustering; Input: "
TOKEN_LIMIT = 500


@memory.cache
def embed_labels(labels):
    prompt_labels = [[INSTRUCTION, label] for label in labels]
    embeddings = embedding_model.encode(prompt_labels)
    return embeddings


def store_variables(idno: str, variables: dict) -> None:
    """
    Store the variables locally in data/microdata/variables/<idno>/<idno>_variables.json
    """
    variables_path = get_idno_fpath(idno)
    variables_path.write_text(json.dumps(variables, indent=2))


class ThemeLLM(object):
    """
    ThemeLLM encapsulates the methods for generating themes from microdata data dictionaries using LLMs.

    The class expects a data dictionary as input. The data dictionary can be provided in two ways:
    - a data dictionary in the form of a JSON file
    - an idno of a study in the form of a string. The data dictionary will be retrieved from a specified NADA catalog.
    """

    def __init__(self, idno: str, data_dictionary: Union[str, Path, dict] = None, catalog_url: str = None, vars_dir: Union[str, Path] = None, desc_dir: Union[str, Path] = None, force: bool = False, persist: bool = True):
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

        self.vars_dir = vars_dir
        self.desc_dir = desc_dir

        self._load_data_dictionary(force=force, persist=persist)

    def _load_data_dictionary(self, force: bool = False, persist: bool = True):
        """
        Load the data dictionary. First, check if the data dictionary is already loaded. If not, check if it is already downloaded.
        """
        variables_path = get_idno_fpath(idno=self.idno, vars_dir=self.vars_dir)

        if isinstance(self.data_dictionary, dict):
            # The data dictionary is already loaded.
            if persist: store_variables(self.idno, self.data_dictionary)
            return

        if self.data_dictionary is None:
            # Check first if there is a local version?
            if variables_path.exists() and not force:
                self.data_dictionary = json.load(open(variables_path, "r"))
                return
            else:
                # The data dictionary is not provided. Load it from the catalog.
                self.data_dictionary = fetch_variables(idno=self.idno, catalog_url=self.catalog_url)

        elif isinstance(self.data_dictionary, (str, Path)):
            # The data dictionary is provided as a path to a JSON file.
            self.data_dictionary = json.load(open(self.data_dictionary, "r"))

        else:
            raise ValueError("The data dictionary must be provided as a path to a JSON file or as a dict.")

        if persist: store_variables(self.idno, self.data_dictionary)

    def semantic_enrichment(self):
        pass

    def semantic_embedding(self):
        pass

    def clustering(self):
        pass

    def __str__(self):
        return "ThemeLLM(theme_id={}, theme_name={}, theme_description={})".format(
            self.theme_id, self.theme_name, self.theme_description
        )
