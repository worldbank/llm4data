from typing import Optional, Any, List
from pydantic import Extra
from llm4data.prompts.base import DatedPrompt
from llm4data import indicator2name


class IndicatorPrompt(DatedPrompt):
    task_label = "IndicatorPrompt"

    indicator_id: Optional[str] = None
    indicator_code: Optional[str] = None
    input_variables: List[str] = ["indicator_name", "context_data"]
    template = (
        "Pretend you are a genius economist. You respond in narrative manner.\n\n"
        "You know this data{indicator_name}\n"
        "{context_data}\n\n"
        "Select only the relevant data when responding to the prompt.\n\n"
        "You always answer the prompt based on the data you know, and show the relevant numbers but not the raw data."
        " You may respond in a different language if asked in the prompt."
        " You approximate in millions or billions, and use correct units: ```{{{{user_content}}}}```"
    )

    def format(self, **kwargs: Any) -> str:
        if "indicator_name" not in kwargs:
            if self.indicator_id is None:
                indicator_name = ":"
            else:
                if self.indicator_code not in indicator2name:
                    raise ValueError(
                        f"indicator_code must be one of {list(indicator2name.keys())}"
                    )

                indicator_name = indicator2name[self.indicator_code][self.indicator_id]
                indicator_name = f" ({indicator_name}):"

            kwargs["indicator_name"] = indicator_name

        return super().format(**kwargs)

    def parse_response(self, response: dict, **kwargs: Any) -> Any:
        return response["content"]
