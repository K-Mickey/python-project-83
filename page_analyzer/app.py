import logging
from http import HTTPStatus
from urllib.parse import urlparse

import validators
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf import CSRFProtect
from psycopg2.errors import UniqueViolation

from page_analyzer import settings
from page_analyzer.database import URLRepository, get_connection

MAX_URL_LENGTH = 255

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.SECRET_KEY
csrf = CSRFProtect(app)

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/urls")
def create_url():
    raw_url = request.form.get("url", "")
    logger.debug("Received URL: %s", raw_url)

    if errors := validate(raw_url):
        logger.debug("Validation errors: %s", errors)
        return render_template(
            "index.html",
            url=raw_url,
            errors=errors,
        ), HTTPStatus.UNPROCESSABLE_CONTENT

    normalized_url = normalize_url(raw_url)
    logger.debug("Normalized URL: %s", normalized_url)

    try:
        with get_connection() as conn:
            url_repository = URLRepository(conn)
            url = url_repository.create(normalized_url)

    except UniqueViolation:
        logger.debug("URL already exists")
        flash("Страница уже существует", "danger")
        return redirect(url_for("index"))

    except Exception as e:
        logger.error("Error during URL insertion: %s", e)
        flash("Произошла ошибка при добавлении страницы", "danger")
        return redirect(url_for("index"))

    flash("Страница успешно добавлена", "success")
    logger.debug("URL successfully inserted into database %s", url)

    return redirect(
        url_for("get_url", url_id=url.id),
        code=HTTPStatus.FOUND,
    )


@app.get("/urls")
def get_urls():
    with get_connection() as conn:
        urls = URLRepository(conn).get()
    logger.debug("Fetched URLs: %s", urls)
    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:url_id>")
def get_url(url_id: int):
    with get_connection() as conn:
        url_repository = URLRepository(conn)
        url = url_repository.get_by_id(url_id)

    if not url:
        logger.debug("URL not found")
        flash("Страница не найдена", "danger")
        return redirect(url_for("get_urls"), code=HTTPStatus.FOUND)

    logger.debug("Fetched URL: %s", url)
    return render_template("url.html", url=url)


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
