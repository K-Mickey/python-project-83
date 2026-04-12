from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, HTTPError

from page_analyzer.utils.checks import check_url


def test_check_url_success():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
        <html>
            <head><title>Title</title></head>
            <body>
                <h1>Header</h1>
                <meta name="description" content="Example description">
                <p>Some content</p>
            </body>
        </html>
        """
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        check = check_url("https://example.com")

    assert check.status_code == 200
    assert check.h1 == "Header"
    assert check.title == "Title"
    assert check.description == "Example description"
    mock_get.assert_called_once_with("https://example.com")
    mock_response.raise_for_status.assert_called_once()


def test_check_url_http_error():
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError("404 Client Error")

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(HTTPError, match="404 Client Error"):
            check_url("https://example.com/notfound")


def test_check_url_connection_error():
    with patch(
        "requests.get", side_effect=ConnectionError("Network unreachable")
    ):
        with pytest.raises(ConnectionError, match="Network unreachable"):
            check_url("https://unreachable.invalid")
