import logging
from http import HTTPStatus

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf import CSRFProtect

from page_analyzer import settings
from page_analyzer.repository import CheckRepository, Database, UrlRepository
from page_analyzer.utils.checks import check_url, sanitize_url_info
from page_analyzer.utils.flash import FlashCategory
from page_analyzer.utils.urls import normalize_url, validate

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.SECRET_KEY
CSRFProtect(app)

database = Database(settings.DATABASE_URL)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/urls")
def create_url():
    raw_url = request.form.get("url", "")
    logger.debug("Received URL: %s", raw_url)

    if errors := validate(raw_url):
        logger.debug("Validation errors: %s", errors)
        flash("Некорректный URL", FlashCategory.DANGER)
        return render_template(
            "index.html",
            url=raw_url,
            errors=errors,
        ), HTTPStatus.UNPROCESSABLE_CONTENT

    normalized_url = normalize_url(raw_url)
    logger.debug("Normalized URL: %s", normalized_url)

    try:
        with database.transaction() as conn:
            repository = UrlRepository(conn)

            if exist_url := repository.get_by_name(normalized_url):
                logger.debug("URL already exists")
                flash("Страница уже существует", FlashCategory.DANGER)
                return redirect(url_for("get_url", url_id=exist_url.id))

            new_url = repository.create(normalized_url)

        logger.debug("URL successfully inserted into database %s", new_url)
        flash("Страница успешно добавлена", FlashCategory.SUCCESS)

    except Exception as e:
        logger.error("Error during URL insertion: %s", e)
        flash("Произошла ошибка при добавлении страницы", FlashCategory.DANGER)
        return redirect(url_for("index"))

    return redirect(
        url_for("get_url", url_id=new_url.id),
        code=HTTPStatus.FOUND,
    )


@app.get("/urls")
def get_urls():
    with database.transaction() as conn:
        urls = UrlRepository(conn).get_all_with_last_checks()

    logger.debug("Fetched URLs: %s", urls)
    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:url_id>")
def get_url(url_id: int):
    with database.transaction() as conn:
        url = UrlRepository(conn).get_by_id(url_id)
        checks = CheckRepository(conn).get_checks_by_url(url_id)

    if not url:
        logger.debug("URL not found")
        flash("Страница не найдена", FlashCategory.DANGER)
        return redirect(url_for("get_urls"), code=HTTPStatus.FOUND)

    logger.debug("Fetched URL: %s", url)
    return render_template(
        "url.html",
        url=url,
        checks=checks,
    )


@app.post("/urls/<int:url_id>/checks")
def create_check(url_id: int):
    try:
        with database.transaction() as conn:
            url = UrlRepository(conn).get_by_id(url_id)
            if not url:
                logger.debug("URL not found")
                flash("Страница не найдена", FlashCategory.DANGER)
                return redirect(
                    url_for("get_urls"),
                    code=HTTPStatus.UNPROCESSABLE_CONTENT,
                )

        url_info = check_url(url.name)
        url_info = sanitize_url_info(url_info)

        with database.transaction() as conn:
            repository = CheckRepository(conn)
            check = repository.create(
                url_id=url_id,
                status_code=url_info.status_code,
                h1=url_info.h1,
                title=url_info.title,
                description=url_info.description,
            )

            logger.debug("Created check: %s", check)
            flash("Страница успешно проверена", FlashCategory.SUCCESS)

    except Exception as e:
        logger.error("Error during check creation: %s", e)
        flash("Произошла ошибка при проверке", FlashCategory.DANGER)

    return redirect(
        url_for("get_url", url_id=url_id),
        code=HTTPStatus.FOUND,
    )
