from datetime import datetime
from typing import Protocol

from psycopg2._psycopg import connection as PsycopgConnection
from psycopg2.extras import NamedTupleCursor


class Url(Protocol):
    id: int
    name: str
    created_at: datetime


class UrlLastCheck(Url):
    last_check_created_at: datetime | None
    last_check_status_code: int | None


class UrlRepository:
    def __init__(self, connection: PsycopgConnection):
        self.connection = connection

    def create(self, name: str) -> Url:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) "
                "RETURNING id, name, created_at",
                (name,),
            )
            return cur.fetchone()

    def get_all_with_last_checks(self) -> list[UrlLastCheck]:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT 
                    urls.id,
                    urls.name,
                    urls.created_at,
                    checks.created_at as last_check_created_at,
                    checks.status_code as last_check_status_code
                FROM urls
                LEFT JOIN (
                    SELECT DISTINCT ON (url_id) url_id, created_at, status_code
                    FROM url_checks
                    ORDER BY url_id, created_at DESC
                ) checks ON urls.id = checks.url_id
                ORDER BY urls.created_at DESC
            """)
            return cur.fetchall()

    def get_by_id(self, url_id: int) -> Url | None:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls WHERE id = %s",
                (url_id,),
            )
            return cur.fetchone()
