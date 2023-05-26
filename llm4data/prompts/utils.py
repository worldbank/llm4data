from openai_tools.prompt import PromptZeros
from llm4data import configs


def get_prompt_manager(task_label: str, type: str = "zeros"):
    if type == "zeros":
        return PromptZeros(
            payloads_dir=configs.dirs.openai_payload_dir,
            task_label=task_label,
        )
    else:
        raise ValueError(f"Invalid type: {type}")
