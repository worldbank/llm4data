"""
Scrape the microdata API for metadata.
"""
import backoff
import requests

from llm4data.configs import base_urls


@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def fetch_variables(idno: str, catalog_url: str = None) -> dict:
    """
    Fetch the microdata variables metadata from the API.
    """
    if catalog_url is None:
        # Use the default catalog URL.
        catalog_url = base_urls.catalog_url

    url = "/".join([catalog_url, "variables", idno])

    response = requests.get(url)

    return response.json()
