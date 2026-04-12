from contextlib import contextmanager
from typing import Generator

from psycopg2._psycopg import connection as PsycopgConnection
from psycopg2.pool import ThreadedConnectionPool


class Database:
    def __init__(
        self,
        minconn: int,
        maxconn: int,
        dsn: str,
    ):
        self._pool = ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=dsn,
        )

    def get_connection(self) -> PsycopgConnection:
        return self._pool.getconn()

    def release_connection(self, connection: PsycopgConnection) -> None:
        self._pool.putconn(connection)

    def close_all(self) -> None:
        self._pool.closeall()

    @contextmanager
    def transaction(self) -> Generator[PsycopgConnection, None, None]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self.release_connection(conn)
