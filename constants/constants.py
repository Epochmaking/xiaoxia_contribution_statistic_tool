import os
import tempfile
import dotenv
from pathlib import Path
from mitmproxy.http import HTTPFlow

dotenv.load_dotenv("config.ini")

LISTEN_PORT = int(os.getenv("listen_port", "8080"))
MAX_TIMEOUT_S = float(os.getenv("max_timeout_s", "10.0"))
MAX_RETRIES = int(os.getenv("max_retries", "3"))
FETCH_INTERVAL_S = float(os.getenv("fetch_interval_s", "1.0"))
MAX_ARTICLE_COUNT_PER_REQUEST = int(os.getenv("max_article_count_per_request", "10"))
LISTEN_HOST = "127.0.0.1"

MAX_LLM_RETRIES = int(os.getenv("max_llm_retries", "3"))
GLM_API_KEY: str | None = os.getenv("glm_api_key", "00ebdd968b7742babfa0a6e04b33a0e4.ZrdN0x9z5M5dbNsq")
LLM_MODEL: str | None = os.getenv("glm_model", "glm-4.7-flash")
LLM_BACKUP_MODEL: str | None = os.getenv("glm_backup_model", "")
LLM_FETCH_INTERVAL_S: float = float(os.getenv("llm_fetch_interval_s", "1.0"))


MP_BIZ: str | None = os.getenv("mp_id", None)
ARTICLE_LIST_URL: str | None = None
ARTICLE_LIST_URL_TEMPLATE: str = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}#wechat_redirect"
TEMPLATE_FLOW: HTTPFlow | None = None

TEMP_PATH = Path(tempfile.gettempdir()) / "xiaoxia_contribution_statistic_tool"
TEMP_CONTEXT_DIR = TEMP_PATH / "temp_context"
TEMP_DB_PATH = TEMP_PATH / "temp_db.db"


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
    "MAX_LLM_RETRIES",
    "GLM_API_KEY",
    "LLM_MODEL",
    "LLM_BACKUP_MODEL",
    "LLM_FETCH_INTERVAL_S",
    "TEMPLATE_FLOW",
    "TEMP_PATH",
    "TEMP_CONTEXT_DIR",
    "TEMP_DB_PATH",
]
