import json
from typing import Union
from pathlib import Path

from .quality import is_valid_variable
from .paths import get_idno_fpath


def get_label_names(idno: str, vars_dir: Union[str, Path] = None):
    """
    This function transforms the data_dictionary/variables into the following structure:

    ```
    {
        "label1": ["vname1"],
        "label2": ["vname2"],
        "label3": ["vname3", "vname3.1"],
    }
    ```
    """
    variables = json.load(open(get_idno_fpath(idno, vars_dir), "r"))
    variables = variables.get("variables", [])

    # Filter out invalid variables.
    variables = sorted(filter(is_valid_variable, variables), key=lambda x: x["labl"])

    # Group variable name that have the same label.
    label_names: dict[str, list] = {}

    for var in variables:
        label = (var.get("labl", var.get("label", "")) or "").strip()
        vname = var.get("name", "")
        if label not in label_names:
            label_names[label] = []

        label_names[label].append(vname)

    return label_names
