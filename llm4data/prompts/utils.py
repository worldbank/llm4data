
import os
from pathlib import Path
from openai_tools.prompt import PromptZeros

from llm4data import configs


openai_payload = os.getenv(configs["dirs"]["OPENAI_PAYLOAD_DIR"])
if openai_payload is None:
    raise ValueError("`OPENAI_PAYLOAD_DIR` environment variable is not set. Consider adding it to your config.toml file.")

openai_payload = Path(openai_payload)


def get_prompt_manager(task_label: str, type: str = "zeros"):
    if type == "zeros":
        return PromptZeros(
            payloads_dir=openai_payload,
            task_label=task_label,
        )
    else:
        raise ValueError(f"Invalid type: {type}")
