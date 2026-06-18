import os
import dotenv

dotenv.load_dotenv("config.ini")

LISTEN_PORT = int(os.getenv("listen_port", "8080"))
MAX_TIMEOUT_S = float(os.getenv("max_timeout_s", "10.0"))
MAX_RETRIES = int(os.getenv("max_retries", "3"))
FETCH_INTERVAL_S = float(os.getenv("fetch_interval_s", "1.0"))

MP_BIZ: str | None = None
ARTICLE_LIST_URL: str | None = None


__all__ = [
    "LISTEN_PORT",
    "MP_BIZ",
    "ARTICLE_LIST_URL",
    "MAX_TIMEOUT_S",
    "MAX_RETRIES",
    "FETCH_INTERVAL_S",
]
