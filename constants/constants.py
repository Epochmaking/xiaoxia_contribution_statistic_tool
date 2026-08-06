from typing import TYPE_CHECKING
import os
import tempfile
from pathlib import Path
import dotenv
from helpers.config_helper import read_xiaoxia_members
if TYPE_CHECKING:
    from mitmproxy.http import HTTPFlow

DEFAULT_CONFIG = """# 提示：如需修改配置，修改完之后请保存文件并重新启动本软件

listen_port=8082 # 监听端口\n
max_article_count_per_request=10 # 每次请求的文章数量，最大10，推荐保持默认\n
max_timeout_s=6 # 最大超时时间，单位秒\n
max_retries=3 # 最大重试次数\n
fetch_interval_s=2 # 每次请求间隔，单位秒，不要调太低防止被微信反爬虫拦截封禁\n

max_llm_retries=99 # 最大语言模型重试次数（用于识别落款信息）\n
llm_fetch_interval_s=1.5 # 每次语言模型调用请求间隔，单位秒\n
glm_api_key='00ebdd968b7742babfa0a6e04b33a0e4.ZrdN0x9z5M5dbNsq' # GLM API密钥\n
glm_model='glm-4.7' # 首选glm-4.7模型\n
glm_backup_model='glm-5' # 备选模型glm-5\n

xiaoxia_members=None # 小夏成员名单，成员间用逗号隔开不要换行，如为空则默认所有人都是小夏\n
fee_base=100 # 稿费基数，单位元\n
"""

TEMP_PATH = Path(tempfile.gettempdir()) / "xiaoxia_contribution_statistic_tool"
TEMP_CONTEXT_DIR = TEMP_PATH / "temp_context"
TEMP_DB_PATH = TEMP_PATH / "temp_db.db"

CONFIG_FILE = TEMP_PATH / "config.ini"

# 若不存在文件，创建默认文件
if not os.path.exists(CONFIG_FILE):
    TEMP_PATH.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_CONFIG)

dotenv.load_dotenv(CONFIG_FILE)


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

XIAOXIA_MEMBERS: list[str] | None = read_xiaoxia_members()
FEE_BASE: int = int(os.getenv("fee_base", "100"))

MP_BIZ: str | None = os.getenv("mp_id", None)
ARTICLE_LIST_URL: str | None = None
ARTICLE_LIST_URL_TEMPLATE: str = "https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}#wechat_redirect"
TEMPLATE_FLOW: "HTTPFlow | None" = None


__all__ = [
    "CONFIG_FILE",
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
    "XIAOXIA_MEMBERS",
    "FEE_BASE",
]