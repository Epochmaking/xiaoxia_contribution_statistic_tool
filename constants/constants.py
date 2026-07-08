import os
import dotenv

dotenv.load_dotenv("config.ini")

LISTEN_PORT = int(os.getenv("listen_port", "8080"))
MAX_TIMEOUT_S = float(os.getenv("max_timeout_s", "10.0"))
MAX_RETRIES = int(os.getenv("max_retries", "3"))
FETCH_INTERVAL_S = float(os.getenv("fetch_interval_s", "1.0"))
MAX_ARTICLE_COUNT_PER_REQUEST = int(os.getenv("max_article_count_per_request", "10"))
LISTEN_HOST = "127.0.0.1"

MP_BIZ: str | None = os.getenv("mp_id", None)
ARTICLE_LIST_URL: str | None = None
ARTICLE_LIST_URL_TEMPLATE: str = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}#wechat_redirect"


__all__ = [
    "LISTEN_PORT",
    "MP_BIZ",
    "ARTICLE_LIST_URL",
    "ARTICLE_LIST_URL_TEMPLATE",
    "MAX_TIMEOUT_S",
    "MAX_RETRIES",
    "FETCH_INTERVAL_S",
    "MAX_ARTICLE_COUNT_PER_REQUEST",
    "LISTEN_HOST",
]
