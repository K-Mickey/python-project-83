from urllib.parse import urlparse

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from page_analyzer import app
from page_analyzer.repository import Database
from page_analyzer.settings import (
    DATABASE_URL,
    MIGRATION_SCRIPT,
)

_parsed = urlparse(DATABASE_URL)
ADMIN_DB = "postgres"
ADMIN_DB_URL = _parsed._replace(path=f"/{ADMIN_DB}").geturl()
DB_NAME = _parsed.path[1:]


@pytest.fixture(scope="session")
def init_database():
    create_test_database(
        admin_dsn=ADMIN_DB_URL,
        test_dbname=DB_NAME,
    )

    create_tables(
        dsn=DATABASE_URL,
        migration_script=MIGRATION_SCRIPT,
    )

    yield

    remove_test_database(
        admin_dsn=ADMIN_DB_URL,
        test_dbname=DB_NAME,
    )


@pytest.fixture
def database():
    yield Database(DATABASE_URL)


@pytest.fixture
def client(init_database):
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        yield client

    with psycopg2.connect(DATABASE_URL) as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("TRUNCATE urls CASCADE;")


def create_test_database(
    admin_dsn: str,
    test_dbname: str,
):
    conn_admin = psycopg2.connect(admin_dsn)
    conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn_admin.cursor() as cur:
        cur.execute("DROP DATABASE IF EXISTS %s;" % test_dbname)
        cur.execute("CREATE DATABASE %s;" % test_dbname)
    conn_admin.close()


def create_tables(
    dsn: str,
    migration_script: str,
):
    conn = psycopg2.connect(dsn)
    with conn.cursor() as cur:
        with open(migration_script, "r") as f:
            cur.execute(f.read())
    conn.commit()
    conn.close()


def remove_test_database(
    admin_dsn: str,
    test_dbname: str,
):
    conn_admin = psycopg2.connect(admin_dsn)
    conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn_admin.cursor() as cur:
        cur.execute(
            """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE datname = '%s'
            AND pid <> pg_backend_pid();
        """
            % test_dbname
        )
        cur.execute("DROP DATABASE IF EXISTS %s;" % test_dbname)
    conn_admin.close()
