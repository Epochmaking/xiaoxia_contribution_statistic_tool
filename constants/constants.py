import dotenv, os

dotenv.load_dotenv("config.ini")

LISTEN_PORT = int(os.getenv("listen_port", "8080"))

MP_BIZ: str | None = None
ARTICLE_LIST_URL: str | None = None


__all__ = [
    "LISTEN_PORT",
    "MP_BIZ",
    "ARTICLE_LIST_URL",
]
