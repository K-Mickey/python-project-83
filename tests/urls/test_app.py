from http import HTTPStatus
from unittest.mock import Mock

from requests import HTTPError

from page_analyzer.utils.flash import FlashCategory


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK


def test_create_url_success(client):
    response = client.post(
        "/urls", data={"url": "https://example.com"}, follow_redirects=False
    )
    assert response.status_code == HTTPStatus.FOUND
    assert "/urls/" in response.headers["Location"]
    response_follow = client.get(response.headers["Location"])
    assert FlashCategory.SUCCESS.value in response_follow.text


def test_create_url_validation_error(client):
    response = client.post("/urls", data={"url": "not_a_url"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert "Некорректный URL" in response.text
    response_all = client.get("/urls")
    assert "not_a_url" not in response_all.text


def test_create_url_duplicate(client):
    client.post("/urls", data={"url": "https://duplicate.com"})
    response = client.post(
        "/urls", data={"url": "https://duplicate.com"}, follow_redirects=False
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == "/"
    response_follow = client.get("/")
    assert FlashCategory.DANGER.value in response_follow.text
    assert "Страница уже существует" in response_follow.text


def test_get_urls_empty(client):
    response = client.get("/urls")
    assert response.status_code == HTTPStatus.OK
    assert "<table" in response.text


def test_get_urls_with_data(client):
    client.post("/urls", data={"url": "https://first.com"})
    client.post("/urls", data={"url": "https://second.com"})
    response = client.get("/urls")
    assert "first.com" in response.text
    assert "second.com" in response.text


def test_get_existing_url(client):
    post_resp = client.post("/urls", data={"url": "https://detail.com"})
    location = post_resp.headers["Location"]
    url_id = location.split("/")[-1]
    response = client.get(f"/urls/{url_id}")
    assert response.status_code == HTTPStatus.OK
    assert "detail.com" in response.text


def test_normalization(client):
    client.post("/urls", data={"url": "HTTPS://Example.COM/any/path?q=1"})
    response = client.get("/urls")
    assert "https://example.com" in response.text
    assert "/any/path" not in response.text


def test_create_check_nonexistent_url(client):
    response = client.post("/urls/99999/checks", follow_redirects=False)

    assert response.headers["Location"] == "/urls"
    follow_response = client.get(response.headers["Location"])
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert FlashCategory.DANGER.value in follow_response.text
    assert "Страница не найдена" in follow_response.text


def test_create_check_success(client, mocker):
    post_resp = client.post("/urls", data={"url": "https://check-success.com"})
    location = post_resp.headers["Location"]
    url_id = location.split("/")[-1]

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><head><title>Success</title></head><body><h1>Header</h1></body></html>"
    mocker.patch("requests.get", return_value=mock_response)

    response = client.post(f"/urls/{url_id}/checks", follow_redirects=False)

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == f"/urls/{url_id}"

    follow_response = client.get(response.headers["Location"])
    assert FlashCategory.SUCCESS.value in follow_response.text
    assert "Страница успешно проверена" in follow_response.text


def test_create_check_network_error(client, mocker):
    post_resp = client.post("/urls", data={"url": "https://unreachable.com"})
    url_id = post_resp.headers["Location"].split("/")[-1]

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
    mocker.patch("requests.get", return_value=mock_response)

    response = client.post(f"/urls/{url_id}/checks", follow_redirects=False)

    assert response.headers["Location"] == f"/urls/{url_id}"

    follow_response = client.get(response.headers["Location"])
    assert FlashCategory.DANGER.value in follow_response.text
    assert "Произошла ошибка при проверке" in follow_response.text
