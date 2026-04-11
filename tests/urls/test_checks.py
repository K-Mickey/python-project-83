from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, HTTPError

from page_analyzer.utils.checks import check_url


def test_check_url_success():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        status = check_url("https://example.com")

    assert status == 200
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
