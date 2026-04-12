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

MIGRATION_SCRIPT = os.getenv("MIGRATION_SCRIPT", "database.sql")
