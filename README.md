# LLM4Data

LLM4Data is a Python library designed to facilitate the application of large language models (LLMs) and artificial intelligence for data and knowledge discovery. It is intended to empower users and organizations to discover and interact with development data in innovative ways through natural language.

Built around existing metadata standards and schemas, users and organizations can benefit from LLMs to enhance data-driven applications, enabling natural language processing, text generation, and more with LLM4Data. The library serves as a bridge between LLMs and development data using open-sourced libraries, offering a seamless interface to leverage the capabilities of these powerful language models.

Key Features and Roadmap:
- Text generation: Utilize LLMs to generate coherent and contextually relevant text around development data, enabling the creation of chatbots and content generation systems.
- Interactive experiences: Create engaging user experiences by integrating LLMs into applications, allowing users to interact with development data in a more intuitive and conversational manner.
- Metadata augmentation: Enhance existing metadata with LLMs, enabling the creation of new metadata and the improvement of existing metadata.
- AI-powered insights: Extract valuable insights from datasets using LLMs, empowering data exploration, trend analysis, and knowledge discovery.
- Natural language processing: Leverage LLMs to analyze and process textual data, enabling tasks like sentiment analysis, text classification, and language translation.
- Dynamic integration: Through the use of metadata standards and schemas, load and utilize your own Python scripts containing LLM functionality on-the-fly, seamlessly incorporating them into your project through plug-ins.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install LLM4Data.

```bash
pip install llm4data
```

## Usage

```python
from llm4data.promps.indicators import wdi

# Create a WDI API prompt object
wdi_api = wdi.WDIAPIPrompt()

# Send a prompt to the LLM to get a WDI API URL relevant to the prompt
response = wdi_api.send_prompt("What is the gdp and the co2 emissions of the philippines and its neighbors in the last decade?")

# Parse the response to get the WDI API URL
wdi_api_url = wdi_api.parse_response(response)
print(wdi_api_url)
```

The output will look like the following:

```
https://api.worldbank.org/v2/country/PHL;IDN;MYS;SGP;THA;VNM/indicator/NY.GDP.MKTP.CD;EN.ATM.CO2E.KT?date=2013:2022&format=json&source=2
```


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License

LLM4Data is licensed under the [ World Bank Master Community License Agreement](LICENSE).
