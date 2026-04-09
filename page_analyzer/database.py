from contextlib import contextmanager
from datetime import datetime
from typing import Protocol

from psycopg2.extras import NamedTupleCursor
from psycopg2.pool import ThreadedConnectionPool

from page_analyzer import settings

pool = ThreadedConnectionPool(
    minconn=settings.DATABASE_MIN_CONN,
    maxconn=settings.DATABASE_MAX_CONN,
    dsn=settings.DATABASE_URL,
)


@contextmanager
def get_connection():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        conn.rollback()
        pool.putconn(conn)


class URL(Protocol):
    id: int
    name: str
    created_at: datetime


class URLRepository:
    def __init__(self, connection):
        self.connection = connection

    def create(self, name: str) -> URL:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) "
                "RETURNING id, name, created_at",
                (name,),
            )
            url = cur.fetchone()

        self.connection.commit()
        return url

    def get(self) -> list[URL]:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
            SELECT id, name, created_at 
            FROM urls 
            ORDER BY created_at DESC
            """)
            urls = cur.fetchall()
        return urls

    def get_by_id(self, url_id: int) -> URL | None:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls WHERE id = %s",
                (url_id,),
            )
            return cur.fetchone()
