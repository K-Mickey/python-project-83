from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass(slots=True)
class URLInfo:
    status_code: int
    h1: str | None
    title: str | None
    description: str | None


def check_url(url: str) -> URLInfo:
    response = requests.get(url)
    response.raise_for_status()

    bs = BeautifulSoup(response.text, 'html.parser')

    h1 = bs.find('h1')
    title = bs.find('title')
    description = bs.find('meta', {'name': 'description'})

    return URLInfo(
        status_code=response.status_code,
        h1=h1.text if h1 else None,
        title=title.text if title else None,
        description=description['content'] if description else None,
    )
