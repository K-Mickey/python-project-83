import os

from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/page_analyzer",
)
DATABASE_MIN_CONN = int(os.getenv("DATABASE_MIN_CONN", "1"))
DATABASE_MAX_CONN = int(os.getenv("DATABASE_MAX_CONN", "10"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv(
    "LOG_FORMAT",
    "> %(asctime)s %(levelname)s [%(filename)s - %(name)s - %(lineno)d] "
    "> %(message)s",
)

TESTING = os.getenv("TESTING", False)
TEST_DB_URL = os.getenv(
    "TEST_BASE_DB_URL", "postgresql://postgres:postgres@localhost:5432/test"
)
TEST_ADMIN_DB = os.getenv("TEST_ADMIN_DB", "postgres")
_parts = TEST_DB_URL.rstrip("/").split("/")
TEST_DB_NAME = _parts[-1]
TEST_ADMIN_DB_URL = "/".join(_parts[:-1] + [TEST_ADMIN_DB])
MIGRATION_SCRIPT = os.getenv("MIGRATION_SCRIPT", "database.sql")
