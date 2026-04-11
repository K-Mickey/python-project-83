import logging
from http import HTTPStatus

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from psycopg2.errors import UniqueViolation

from page_analyzer.repository import URLRepository
from page_analyzer.utils.flash import FlashCategory
from page_analyzer.utils.urls import normalize_url, validate

bp = Blueprint(
    name="urls",
    import_name=__name__,
    template_folder="templates",
)
logger = logging.getLogger(__name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/urls")
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
        with current_app.database.transaction() as conn:
            url_repository = URLRepository(conn)
            url = url_repository.create(normalized_url)

        logger.debug("URL successfully inserted into database %s", url)
        flash("Страница успешно добавлена", FlashCategory.SUCCESS)

    except UniqueViolation:
        logger.debug("URL already exists")
        flash("Страница уже существует", FlashCategory.DANGER)
        return redirect(url_for("urls.index"))

    except Exception as e:
        logger.error("Error during URL insertion: %s", e)
        flash("Произошла ошибка при добавлении страницы", FlashCategory.DANGER)
        return redirect(url_for("urls.index"))

    return redirect(
        url_for("urls.get_url", url_id=url.id),
        code=HTTPStatus.FOUND,
    )


@bp.get("/urls")
def get_urls():
    with current_app.database.transaction() as conn:
        urls = URLRepository(conn).get()
    logger.debug("Fetched URLs: %s", urls)
    return render_template("urls.html", urls=urls)


@bp.get("/urls/<int:url_id>")
def get_url(url_id: int):
    with current_app.database.transaction() as conn:
        url_repository = URLRepository(conn)
        url = url_repository.get_by_id(url_id)

    if not url:
        logger.debug("URL not found")
        flash("Страница не найдена", FlashCategory.DANGER)
        return redirect(url_for("urls.get_urls"), code=HTTPStatus.FOUND)

    logger.debug("Fetched URL: %s", url)
    return render_template("url.html", url=url)
