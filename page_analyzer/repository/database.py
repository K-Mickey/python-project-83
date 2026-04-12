from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2._psycopg import connection as PsycopgConnection


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def get_connection(self) -> PsycopgConnection:
        return psycopg2.connect(self.dsn)

    @staticmethod
    def close_connection(connection: PsycopgConnection) -> None:
        connection.close()

    @contextmanager
    def transaction(self) -> Generator[PsycopgConnection, None, None]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.close_connection(conn)
