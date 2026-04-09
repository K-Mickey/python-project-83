import logging
import os
from contextlib import contextmanager
from datetime import datetime
from typing import NamedTuple
from urllib.parse import urlparse

import validators
from dotenv import load_dotenv
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
from psycopg2.pool import SimpleConnectionPool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MAX_URL_LENGTH = 255

logging.basicConfig(level="DEBUG")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
csrf = CSRFProtect(app)


pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL,
)


class URL(NamedTuple):
    id: int
    name: str
    created_at: datetime


@contextmanager
def get_connection():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


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
        ), 422

    normalized_url = normalize_url(raw_url)
    logger.debug("Normalized URL: %s", normalized_url)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO urls (name) VALUES (%s) "
                    "RETURNING id, created_at",
                    (normalized_url,),
                )
                url_id, created_at = cur.fetchone()

            conn.commit()

    except UniqueViolation:
        logger.debug("URL already exists")
        flash("Такая ссылка уже существует", "danger")
        return redirect(url_for("index"))

    except Exception as e:
        logger.error("Error during URL insertion: %s", e)
        flash("Произошла ошибка при добавлении ссылки", "danger")
        return redirect(url_for("index"))

    url = URL(
        id=url_id,
        name=normalized_url,
        created_at=created_at,
    )

    flash("Ссылка успешно добавлена", "success")
    logger.debug("URL successfully inserted into database %s", url)

    return redirect(url_for("get_url", url_id=url.id), code=303)


@app.get("/urls")
def get_urls():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM urls")
            urls = cur.fetchall()

    urls = [URL(*url) for url in urls]
    logger.debug("Fetched URLs: %s", urls)
    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:url_id>")
def get_url(url_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM urls WHERE id = %s", (url_id,))
            url = cur.fetchone()

    if not url:
        logger.debug("URL not found")
        flash("Ссылка не найдена", "danger")
        return redirect(url_for("get_urls"), code=303)

    url = URL(*url)
    logger.debug("Fetched URL: %s", url)
    return render_template("url.html", url=url)


def validate(url: str) -> dict[str, list[str]]:
    errors = {}
    if not validators.url(url):
        errors.setdefault("url", []).append("Некорректная ссылка")
    if len(url) > MAX_URL_LENGTH:
        errors.setdefault("url", []).append(
            f"Ссылка не должна превышать {MAX_URL_LENGTH} символов"
        )
    return errors


def normalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    normalized = f"{parsed.scheme}://{parsed.netloc}"
    return normalized.lower()
