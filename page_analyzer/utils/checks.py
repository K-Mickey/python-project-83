from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

MAX_TEXT_LENGTH = 200


@dataclass(slots=True)
class UrlInfo:
    status_code: int
    h1: str | None
    title: str | None
    description: str | None


def check_url(url: str) -> UrlInfo:
    response = requests.get(url)
    response.raise_for_status()

    bs = BeautifulSoup(response.text, "html.parser")

    h1 = bs.find("h1")
    title = bs.find("title")
    description = bs.find("meta", {"name": "description"})

    return UrlInfo(
        status_code=response.status_code,
        h1=h1.text if h1 else None,
        title=title.text if title else None,
        description=description["content"] if description else None,
    )


def truncate_string(text: str | None) -> str | None:
    if text is None:
        return None
    if len(text) > MAX_TEXT_LENGTH:
        return text[:MAX_TEXT_LENGTH] + "..."
    return text


def sanitize_url_info(info: UrlInfo) -> UrlInfo:
    return UrlInfo(
        status_code=info.status_code,
        h1=truncate_string(info.h1),
        title=truncate_string(info.title),
        description=truncate_string(info.description),
    )
