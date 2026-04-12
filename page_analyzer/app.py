import logging

from flask import Flask
from flask_wtf import CSRFProtect

from page_analyzer import settings
from page_analyzer.repository import Database
from page_analyzer.views import bp


def create_app(
    database: Database | None = None,
    config: dict | None = None,
) -> Flask:

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
    )

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY

    if config:
        app.config.update(config)

    CSRFProtect(app)

    if not database:
        database = Database(
            minconn=settings.DATABASE_MIN_CONN,
            maxconn=settings.DATABASE_MAX_CONN,
            dsn=settings.DATABASE_URL,
        )

    app.database = database

    app.register_blueprint(bp)

    return app
