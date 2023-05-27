import json
from typing import Any
from urllib.parse import urlparse
from openai_tools.parser import parse_misparsed
from llm4data.prompts.base import DatedPrompt


class WDISQLPrompt(DatedPrompt):
    task_label = "WDISQLPrompt"

    def __init__(self, input_variables=None, template=None):
        if template is None and input_variables is None:
            input_variables = ["now", "table", "fields"]
            template = (
                "Current date: {now}\n\n"
                "I have a database containing data from the WDI indicators."
                " Write an SQL query for the prompt: ```{{{{user_content}}}}```\n\n"
                "table: {table}\n"
                "fields: {fields}\n\n"
                " Use the convention `:param` and not `?`."
                " Use country_iso3 when querying, use country in the result.\n\n"
                "Use the last 10 years if no year is specified."
                " Drop rows with no value.\n\n"
                "Return the entire row if useful for the prompt."
                " If it will help in the analysis and if it makes sense, always add the year in the `SELECT` clause if it is not already there.\n\n"
                """Return the output as JSON for json.loads: {{"query_string": <SQL>}}"""
            )

        super().__init__(input_variables=input_variables, template=template)

    def parse_response(self, response: dict, **kwargs: Any) -> Any:
        try:
            content = parse_misparsed(
                response["content"].strip(),
                open="{",
                close="}",
                normalize_newline=True,
                to_json=True,
            )
            query_string = content["query_string"]
        except json.JSONDecodeError:
            query_string = response["content"].strip()

        return query_string


class WDIAPIPrompt(DatedPrompt):
    """Context for generating a WDI API URL from a prompt.

    Example API URL:
        - https://api.worldbank.org/v2/country/PHL;IDN;MYS;SGP;THA;VNM/indicator/NY.GDP.MKTP.CD;EN.ATM.CO2E.KT?date=2013:2022&format=json&source=2
    """

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

    def get_indicator_code_from_url(url):
        """
        Get the indicator code from a WDI API URL.
        """
        parsed = urlparse(url)
        path = parsed.path
        path = path.split("/")

        if "indicator" in path:
            return path[path.index("indicator") + 1]
        else:
            return None

    def parse_response(
        self, response: dict, per_page: int = 10000, **kwargs: Any
    ) -> Any:
        endpoint = response["content"].strip()

        if "None" in endpoint:
            endpoint = None
        else:
            endpoint = endpoint + f"&per_page={per_page}"

        return endpoint
