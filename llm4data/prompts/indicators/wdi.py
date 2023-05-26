from datetime import datetime
from typing import Any
from langchain.prompts.prompt import PromptTemplate
from llm4data import indicator2name


class WDISQLPromptTemplate(PromptTemplate):

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

    def format(self, **kwargs: Any) -> str:
        if "now" not in kwargs:
            kwargs["now"] = datetime.now().date()

        return super().format(**kwargs)

    # def llm2sql(self, prompt):
    #     now = datetime.now().date()
    #     table = self.__tablename__
    #     fields = ", ".join(self.__llm_fields__)
