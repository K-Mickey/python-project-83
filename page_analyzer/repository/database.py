from contextlib import contextmanager

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

    def connection(self):
        return self._pool.getconn()

    def close_connection(self, connection):
        self._pool.putconn(connection)

    def close(self):
        self._pool.closeall()

    @contextmanager
    def transaction(self):
        conn = self.connection()
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            self.close_connection(conn)
