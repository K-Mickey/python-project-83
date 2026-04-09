import logging
import os

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

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MAX_URL_LENGTH = 255

logging.basicConfig(level="DEBUG")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
csrf = CSRFProtect(app)

conn = psycopg2.connect(DATABASE_URL)


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
        )

    flash("Ссылка успешно добавлена", "success")

    return redirect(url_for("index"), code=302)


def validate(url: str) -> dict[str, list[str]]:
    errors = {}
    if not validators.url(url):
        errors.setdefault("url", []).append("Некорректная ссылка")
    if len(url) > MAX_URL_LENGTH:
        errors.setdefault("url", []).append(
            f"Ссылка не должна превышать {MAX_URL_LENGTH} символов"
        )
    return errors
