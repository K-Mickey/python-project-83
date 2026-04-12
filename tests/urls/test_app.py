from http import HTTPStatus
from unittest.mock import Mock

from requests import HTTPError

from page_analyzer.repository import CheckRepository, UrlRepository


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK


def test_create_url_success(client, connection):
    response = client.post(
        "/urls", data={"url": "https://example.com"}, follow_redirects=False
    )
    assert "/urls/" in response.headers["Location"]

    response_follow = client.get(response.headers["Location"])
    assert "Страница успешно добавлена" in response_follow.text
    assert 'data-test="url"' in response_follow.text
    assert 'data-test="checks"' in response_follow.text

    url_id = response.headers["Location"].split("/")[-1]
    with connection.transaction() as conn:
        url = UrlRepository(conn).get_by_id(url_id)

    assert url.name == "https://example.com"


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
    assert "/urls/" in response.headers["Location"]
    response_follow = client.get(response.headers["Location"])
    assert "Страница уже существует" in response_follow.text
    assert 'data-test="url"' in response_follow.text


def test_get_urls_empty(client, connection):
    response = client.get("/urls")
    assert response.status_code == HTTPStatus.OK
    assert 'data-test="urls"' in response.text

    with connection.transaction() as conn:
        urls = UrlRepository(conn).get_all_with_last_checks()
    assert len(urls) == 0


def test_get_urls_with_data(client):
    client.post("/urls", data={"url": "https://first.com"})
    client.post("/urls", data={"url": "https://second.com"})
    response = client.get("/urls")
    assert "https://first.com" in response.text
    assert "https://second.com" in response.text
    assert 'data-test="urls"' in response.text


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
    assert "Страница не найдена" in follow_response.text


def test_create_check_success(client, mocker, connection):
    post_resp = client.post("/urls", data={"url": "https://check-success.com"})
    location = post_resp.headers["Location"]
    url_id = location.split("/")[-1]

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
        <html><head><title>Unique title</title></head>
        <body><h1>Great header</h1></body></html>
        """
    mocker.patch("requests.get", return_value=mock_response)

    response = client.post(f"/urls/{url_id}/checks", follow_redirects=False)
    assert response.headers["Location"] == f"/urls/{url_id}"

    follow_response = client.get(response.headers["Location"])
    assert "Страница успешно проверена" in follow_response.text
    assert 'data-test="url"' in follow_response.text
    assert 'data-test="checks"' in follow_response.text
    assert "Unique title" in follow_response.text
    assert "Great header" in follow_response.text

    with connection.transaction() as conn:
        checks = CheckRepository(conn).get_checks_by_url(int(url_id))

    assert len(checks) == 1
    check = checks[0]
    assert check.url_id == int(url_id)
    assert check.status_code == 200
    assert check.h1 == "Great header"
    assert check.title == "Unique title"
    assert check.description is None


def test_create_check_network_error(client, mocker, connection):
    post_resp = client.post("/urls", data={"url": "https://unreachable.com"})
    url_id = post_resp.headers["Location"].split("/")[-1]

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
    mocker.patch("requests.get", return_value=mock_response)

    response = client.post(f"/urls/{url_id}/checks", follow_redirects=False)
    assert response.headers["Location"] == f"/urls/{url_id}"

    follow_response = client.get(response.headers["Location"])
    assert "Произошла ошибка при проверке" in follow_response.text

    with connection.transaction() as conn:
        checks = CheckRepository(conn).get_checks_by_url(int(url_id))
    assert len(checks) == 0
