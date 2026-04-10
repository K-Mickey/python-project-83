from datetime import datetime
from typing import Protocol

from psycopg2.extras import NamedTupleCursor


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
            return cur.fetchone()

    def get(self) -> list[URL]:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
            SELECT id, name, created_at 
            FROM urls 
            ORDER BY created_at DESC
            """)
            return cur.fetchall()

    def get_by_id(self, url_id: int) -> URL | None:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls WHERE id = %s",
                (url_id,),
            )
            return cur.fetchone()
