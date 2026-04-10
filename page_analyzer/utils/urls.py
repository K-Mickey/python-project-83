from urllib.parse import urlparse

import validators

MAX_URL_LENGTH = 255


def validate(url: str) -> dict[str, list[str]]:
    errors = {}
    if not validators.url(url):
        errors.setdefault("url", []).append("Некорректный URL")
    if len(url) > MAX_URL_LENGTH:
        errors.setdefault("url", []).append(
            f"URL не должен превышать {MAX_URL_LENGTH} символов"
        )
    return errors


def normalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    normalized = f"{parsed.scheme}://{parsed.netloc}"
    return normalized.lower()
