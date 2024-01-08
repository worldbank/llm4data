import uuid
import hashlib
from joblib import Memory
from llm4data.configs import dirs

memory = Memory((dirs.llm4data_cache_dir / "system").as_posix(), verbose=0)


def get_uuid(code: str, as_string: bool = True) -> str:
    """Generate a UUID from the series code.
    """

    uid = uuid.UUID(hashlib.md5(code.encode("utf-8")).hexdigest())
    if as_string:
        return str(uid)

    return uid
