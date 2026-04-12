import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from page_analyzer import create_app
from page_analyzer.repository import Database
from page_analyzer.settings import (
    DATABASE_MAX_CONN,
    DATABASE_MIN_CONN,
    MIGRATION_SCRIPT,
    TEST_ADMIN_DB_URL,
    TEST_DB_NAME,
    TEST_DB_URL,
)


@pytest.fixture(scope="session")
def database():
    create_test_database(
        admin_dsn=TEST_ADMIN_DB_URL,
        test_dbname=TEST_DB_NAME,
    )

    create_tables(
        dsn=TEST_DB_URL,
        migration_script=MIGRATION_SCRIPT,
    )

    yield

    remove_test_database(
        admin_dsn=TEST_ADMIN_DB_URL,
        test_dbname=TEST_DB_NAME,
    )


@pytest.fixture
def connection(database):
    dsn = TEST_DB_URL
    db = Database(
        minconn=DATABASE_MIN_CONN,
        maxconn=DATABASE_MAX_CONN,
        dsn=dsn,
    )

    yield db

    db.close_all()

    with psycopg2.connect(dsn) as conn:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("TRUNCATE urls CASCADE;")


@pytest.fixture
def client(connection):
    app = create_app(
        database=connection,
        config={
            "WTF_CSRF_ENABLED": False,
        },
    )
    with app.test_client() as client:
        yield client


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
