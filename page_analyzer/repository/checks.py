from datetime import datetime
from typing import Protocol

from psycopg2.extras import NamedTupleCursor


class Check(Protocol):
    id: int
    url_id: int
    status_code: int | None
    h1: str | None
    title: str | None
    description: str | None
    created_at: datetime


class CheckRepository:
    def __init__(self, connection):
        self.connection = connection

    def create(
        self,
        url_id: int,
        status_code: int,
    ) -> Check:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                """
                INSERT INTO url_checks (url_id, status_code)
                VALUES (%s, %s)
                RETURNING *
            """
                % (url_id, status_code)
            )
            return cur.fetchone()

    def get_checks_by_url(self, url_id: int) -> list[Check]:
        with self.connection.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                """
                SELECT *
                FROM url_checks
                WHERE url_id = %s
                ORDER BY created_at DESC
            """
                % url_id
            )
            return cur.fetchall()
