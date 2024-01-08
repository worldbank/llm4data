from typing import Union
from pathlib import Path
from llm4data.configs import dirs


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a path.
    """
    if isinstance(path, str):
        path = Path(path)

    return path.resolve()


def get_desc_dir(desc_dir: Union[str, Path] = None) -> Path:
    """
    Returns the path to the directory where the descriptions are stored. If the directory does not exist, it is created.
    If desc_dir is None, the default directory is used.
    """
    if desc_dir is None:
        desc_dir = dirs.microdata_desc_dir

    return normalize_path(desc_dir)


def get_vars_dir(vars_dir: Union[str, Path] = None) -> Path:
    """
    Returns the path to the directory where the variables are stored. If the directory does not exist, it is created.
    If vars_dir is None, the default directory is used.
    """
    if vars_dir is None:
        vars_dir = dirs.microdata_vars_dir

    return normalize_path(vars_dir)



def get_idno_fpath(idno: str, vars_dir: Union[str, Path] = None) -> Path:
    """
    Get the path to the variables file for a given idno.
    """
    variables_dir = get_vars_dir(vars_dir) / idno
    variables_dir.mkdir(parents=True, exist_ok=True)

    variables_path = variables_dir / f"{idno}_variables.json"

    return variables_path


def get_idno_cluster_fpath(idno: str, vars_dir: Union[str, Path] = None) -> Path:
    """
    Get the path to the variables file for a given idno.
    """
    path = get_vars_dir(vars_dir) / idno / f"{idno}_cluster.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    return path


def get_idno_prompt_fpath(idno: str, vars_dir: Union[str, Path] = None) -> Path:
    """
    Get the path to the variables file for a given idno.
    """
    path = get_vars_dir(vars_dir) / idno / f"{idno}_prompt.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    return path


def get_idno_description_fpath(idno: str, desc_dir: Union[str, Path] = None) -> Path:
    """
    Get the path to the variables file for a given idno.
    """
    path = get_desc_dir(desc_dir) / idno / f"{idno}_description.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    return path
