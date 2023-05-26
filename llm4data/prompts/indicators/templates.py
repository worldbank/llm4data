from langchain.prompts.prompt import PromptTemplate
from llm4data import indicator2name

class IndicatorTemplate:
    system = PromptTemplate(
        input_variables=["indicator_name", "sample_data"],
        template="""Pretend you are a genius economist. You respond in narrative manner.

You know this data{indicator_name}
{sample_data}

Select only the relevant data when responding to the prompt.""")
    user = PromptTemplate(
        input_variables=["prompt"],
        template="""You always answer the prompt based on the data you know, and show the relevant numbers but not the raw data. You may respond in a different language if asked in the prompt. You approximate in millions or billions, and use correct units: ```{prompt}```""")

    def __init__(self, prompt: str, sample_data: str, indicator_code: str = None,  indicator_id: str = None):
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
        self.sample_data = sample_data

    def render(self, user: bool = False):
        if user:
            return self.user.render(prompt=self.prompt)
        else:
            return self.system.render(indicator_name=self.indicator_name, sample_data=self.sample_data)
