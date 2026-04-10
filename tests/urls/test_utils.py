import pytest

from page_analyzer.utils.urls import MAX_URL_LENGTH, normalize_url, validate


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://sub.domain.com:8000",
        "https://example.com/path?query=1",
        "https://example.com#fragment",
        "https://"
        + ".".join(
            [
                "a" * 63,
                "b" * 63,
                "c" * 63,
                "d" * 51,
            ]
        )
        + ".com",
    ],
)
def test_valid_urls(url):
    assert validate(url) == {}


@pytest.mark.parametrize(
    "url",
    [
        "not_a_url",
        "http://",
        "https://example..com",
    ],
)
def test_invalid_urls(url):
    errors = validate(url)
    assert "url" in errors
    assert "Некорректный URL" in errors["url"]


@pytest.mark.parametrize(
    "url",
    [
        "https://" + "a" * (MAX_URL_LENGTH - 7),
        "a" * (MAX_URL_LENGTH + 10),
        "https://"
        + ".".join(
            [
                "a" * 63,
                "b" * 63,
                "c" * 63,
                "d" * 52,
            ]
        )
        + ".com",
    ],
)
def test_length_validation(url):
    assert "url" in validate(url)
    assert (
        f"URL не должен превышать {MAX_URL_LENGTH} символов"
        in validate(url)["url"]
    )


@pytest.mark.parametrize(
    "raw_url, expected",
    [
        ("https://example.com", "https://example.com"),
        ("HTTP://EXAMPLE.COM", "http://example.com"),
        ("https://Example.com/Path?query=1#fragment", "https://example.com"),
        ("http://localhost:3000/api", "http://localhost:3000"),
        ("https://sub.domain.com/", "https://sub.domain.com"),
    ],
)
def test_normalize(raw_url, expected):
    assert normalize_url(raw_url) == expected
