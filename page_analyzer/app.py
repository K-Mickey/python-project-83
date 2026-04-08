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

load_dotenv()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")
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

    if not validators.url(url):
        flash("Invalid URL", "danger")
    else:
        flash("URL created", "success")

    return redirect(url_for("index"), code=302)
