import logging
import os
from contextlib import contextmanager

import psycopg2
import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
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


@contextmanager
def get_connection():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


@app.get("/")
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "index.html",
        messages=messages,
    )


@app.post("/urls")
def create_url():
    url = request.form.get("url", "")

    if errors := validate(url):
        logger.debug("Validation errors: %s", errors)
        return render_template(
            "index.html",
            url=url,
            errors=errors,
        ), 422

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO urls (url) VALUES (%s)",
                    (url,),
                )
            conn.commit()

    except UniqueViolation:
        logger.debug("URL already exists")
        flash("Такая ссылка уже существует", "danger")
        return redirect(url_for("index"))

    except Exception as e:
        logger.error("Error during URL insertion: %s", e)
        flash("Произошла ошибка при добавлении ссылки", "danger")
        return redirect(url_for("index"))

    flash("Ссылка успешно добавлена", "success")

    return redirect(url_for("index"), code=303)


def validate(url: str) -> dict[str, list[str]]:
    errors = {}
    if not validators.url(url):
        errors.setdefault("url", []).append("Некорректная ссылка")
    if len(url) > MAX_URL_LENGTH:
        errors.setdefault("url", []).append(
            f"Ссылка не должна превышать {MAX_URL_LENGTH} символов"
        )
    return errors
