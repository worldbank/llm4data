from langchain.prompts.prompt import PromptTemplate
from llm4data import indicator2name


class IndicatorPromptTemplate:
    system = PromptTemplate(
        input_variables=["indicator_name", "context_data"],
        template=("Pretend you are a genius economist. You respond in narrative manner.\n\n"
                  "You know this data{indicator_name}\n"
                  "{context_data}\n\n"
                  "Select only the relevant data when responding to the prompt.")
    )

    user = PromptTemplate(
        input_variables=["prompt"],
        template=("You always answer the prompt based on the data you know, and show the relevant numbers but not the raw data."
                  " You may respond in a different language if asked in the prompt."
                  " You approximate in millions or billions, and use correct units: ```{prompt}```""")
    )

    def __init__(self, prompt: str = None, context_data: str = None, indicator_code: str = None,  indicator_id: str = None):
        if indicator_id is None:
            indicator_name = ":"
        else:
            if indicator_code not in indicator2name:
                raise ValueError(f"indicator_code must be one of {list(indicator2name.keys())}")

            indicator_name = indicator2name[indicator_code][indicator_id]
            indicator_name = f" ({indicator_name}):"

        self.indicator_id = indicator_id
        self.indicator_name = indicator_name
        self.prompt = prompt
        self.context_data = context_data

    def format_prompt(self, user: bool = False):
        if user:
            return self.user.format_prompt(prompt=self.prompt)
        else:
            return self.system.format_prompt(indicator_name=self.indicator_name, context_data=self.context_data)

    def build_message(self):
        return [
            dict(role="system", content=self.format_prompt(user=False).text),
            dict(role="user", content=self.format_prompt(user=True).text)
        ]
