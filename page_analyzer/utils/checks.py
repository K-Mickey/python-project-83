import requests


def check_url(url: str) -> int:
    response = requests.get(url)
    response.raise_for_status()
    return response.status_code
