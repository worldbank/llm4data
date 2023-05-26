from datetime import datetime
from typing import Any
from langchain.prompts.prompt import PromptTemplate
from llm4data import indicator2name
from llm4data.prompts.utils import get_prompt_manager


class DatedPromptTemplate(PromptTemplate):
    task_label = "wdi"
    prompt_type = "zeros"

    def format(self, **kwargs: Any) -> str:
        if "now" not in kwargs:
            kwargs["now"] = datetime.now().date()

        return super().format(**kwargs)

    def send_prompt(self, prompt: str, api_kwargs: dict = None, **kwargs: Any):
        prompt_manager = get_prompt_manager(
            self.task_label,
            type=self.prompt_type,
        )

        return prompt_manager.send_prompt(
            user_content=prompt,
            user_template=self.format(**kwargs),
            return_data=True,
            api_kwargs=api_kwargs,
        )


class WDISQLPromptTemplate(DatedPromptTemplate):
    task_label = "WDISQLPrompt"

    def __init__(self, input_variables=None, template=None):
        if template is None and input_variables is None:
            input_variables = ["now", "table", "fields"]
            template = ("Current date: {now}\n\n"
                        "I have a database containing data from the WDI indicators."
                        " Write an SQL query for the prompt: ```{{{{user_content}}}}```\n\n"
                        "table: {table}\n"
                        "fields: {fields}\n\n"
                        "Only the indicator can parameterized and you must fill the rest."
                        " Use the convention :indicator and not `?`."
                        " Use country_iso3 when querying, use country in the result.\n\n"
                        "Use the last 10 years if no year is specified."
                        " Drop rows with no value.\n\n"
                        "Return the entire row if useful for the prompt."
                        " If it will help in the analysis and if it makes sense, always add the year in the `SELECT` clause if it is not already there.\n\n"
                        """Return the output as JSON for json.loads: {{"query_string": <SQL>}}""")

        super().__init__(input_variables=input_variables, template=template)


class WDIAPIPromptTemplate(DatedPromptTemplate):
    task_label = "WDIAPIPrompt"

    def __init__(self, input_variables=None, template=None):
        if template is None and input_variables is None:
            input_variables = ["now"]

            template = (
                "Current date: {now}\n\n"
                "Generate the relevant API endpoint to answer the prompt: ```{{{{user_content}}}}```\n\n"
                "- If access to the World Bank indicators API is not applicable for the prompt.\n"
                "return: `None`\n"
                "- Do not attempt to generate an API endpoint if the prompt does not ask for an indicator.\n"
                "return: `None`\n"
                "- Do not attempt to generate an API endpoint if the prompt implies conceptual information related to an indicator.\n"
                "return: `None`\n"
                "- Else\n"
                "return: Your response must only be the completed and valid API URL: https://api.worldbank.org/v2/...&format=json\n\n"
                "Always add `source=...` to the URL if multiple indicators are in the URL.\n\n"
                "Do not explain."
            )

        super().__init__(input_variables=input_variables, template=template)
