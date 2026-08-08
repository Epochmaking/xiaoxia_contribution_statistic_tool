# 小夏贡献统计工具 - 技术文档

## 一、技术栈总览


| 类别          | 技术方案                | 版本/说明                                      |
| ------------- | ----------------------- | ---------------------------------------------- |
| 编程语言      | Python                  | 3.12+（基于类型提示）                          |
| 包管理        | uv                      | 依赖锁定与虚拟环境管理                         |
| 编译打包      | Nuitka                  | 单文件/独立目录，PySide6/Playwright 插件       |
| 图形界面      | PySide6 + Qt Designer   | UI 描述文件 → Python 代码编译                 |
| 数据库        | SQLite + SQLAlchemy 2.x | 本地轻量存储（临时文件）                       |
| 抓包/流量分析 | mitmproxy               | HTTP/HTTPS 透明代理                            |
| 页面爬虫      | Playwright              | Chromium 无头浏览器驱动                        |
| 大语言模型    | 智谱 GLM API            | 首选 glm-4.7，备选 glm-5，支持 JSON 结构化输出 |

### 核心依赖（pyproject.toml）

```toml
pyside6>=6.11.1         # Qt 6 跨平台 GUI
mitmproxy>=11.1.3       # 中间人代理工具
playwright>=1.61.0      # 浏览器自动化
sqlalchemy>=2.0.51      # ORM 框架
requests>=2.34.2        # HTTP 请求
openpyxl>=3.1.5         # Excel 导出
dotenv>=0.9.9           # .env 配置解析
nuitka>=4.1.3           # 打包为可执行文件
pathlib>=1.0.1          # 路径操作
```

---

## 二、目录结构与模块职责

```
xiaoxia_contribution_statistic_tool/
├── 小夏推送统计工具.py          # 应用入口：启动 QApplication 与 MainWindow
├── build.py                   # Nuitka 打包脚本（--standalone + 浏览器数据智能嵌入）
├── pyproject.toml             # 项目依赖配置
├── xiaoxia_tool_config.ini    # 运行时配置文件（自动生成，含 BIZ、API Key 等）
│
├── constants/                 # 全局常量
│   └── constants.py           # 监听端口、超时、API Key、临时目录、全局状态变量
│
├── controllers/               # 业务控制器（线程与流程控制）
│   ├── proxy.py               # Windows 系统代理开关（注册表 + WinInet 刷新）
│   ├── crawler.py             # mitmproxy 爬虫基类、BIZ 抓取、文章列表分页抓取
│   ├── content_crawler.py     # Playwright 浏览器自动化：文章内容爬取、人机验证处理
│   ├── analyse.py             # 稿费分析
│   ├── export.py              # Excel 导出（openpyxl）
│   └── threads.py             # QThread 工作线程：GetMpBizThread / GetArticleListThread / GetArticleContentThread
│
├── database/                  # 数据持久化
│   └── db.py                  # SQLAlchemy 引擎初始化、会话获取（临时文件 SQLite）
│
├── models/                    # 数据模型
│   ├── base_model.py          # 声明式 Base 类 + to_dict 序列化
│   ├── article_models.py      # Article ORM 模型（标题、作者、阅读量等字段）
│   ├── mapping.py             # 字段中文映射表 + 文章类型映射表
│   └── ui_models.py           # ArticleListViewModel（QStandardItemModel）+ HyperlinkDelegate
│
├── ui/                        # 图形界面
│   ├── ui_components.py       # MainWindow 主窗口类（无边框+透明+拖动+步骤流程控制）
│   ├── ui_helper.py           # 表格样式初始化（QSS + 列宽/滚动配置）
│   ├── ui_design/main_win.ui  # Qt Designer 布局描述文件
│   └── ui_compiled/main_win.py# compile_ui.py 自动生成的 Python 布局代码
│
├── helpers/                   # 辅助函数
│   ├── helpers.py             # 核心业务：解析文章列表、阅读量接口请求、数据库读写
│   └── config_helper.py       # dotenv 配置读写（写入/删除 mp_id 等）
│
├── utils/                     # 工具函数
│   ├── logging.py             # 彩色控制台日志 + 文件日志（app.log）
│   ├── format.py              # 自定义 JSON 格式化（数组同行紧凑显示）
│   └── compile_ui.py          # 编译 .ui 文件为 .py
│
├── llm/                       # 大语言模型相关
│   ├── llm_parse.py           # GLM API 调用：文末落款提取 + 作者名单结构化
│   └── prepare_dataset.py     # SFT 微调数据集准备脚本（采集文末纯文本）
│
├── exceptions/                # 自定义异常
│   └── exceptions.py          # AnalyseThreadError / GetArticleContentError
│
└── assets/                    # 静态资源
    └── mitmproxy-ca-cert.p12  # mitmproxy 证书
```

---

## 三、核心流程与数据流

### 3.1 总体业务流程（GUI 步骤驱动）

```
步骤一：获取公众号 BIZ
  │
  ▼
步骤二：抓取文章列表（按目标月份过滤）
  │
  ▼
步骤三：逐篇爬取文章内容 + 阅读量 + 作者落款
  │
  ▼
步骤四：在表格中展示 + 导出 Excel
```

### 3.2 详细数据流

#### 步骤一：获取 BIZ

```
GUI (MainWindow.step_one_btn_on_click)
  └─► GetMpBizThread.start()
       └─► MpBizCrawler.start()
            └─► set_network_proxy(LISTEN_HOST, LISTEN_PORT)  # 设置 Windows 全局代理
            └─► mitmproxy DumpMaster 启动，监听 8082 端口
            └─► 用户在微信客户端访问公众号，产生流量
                 └─► MpBizResponseHandler.response()  捕获请求中的 __biz 参数
            └─► 捕获成功后：consts.MP_BIZ = biz
            └─► write_config({"mp_id": biz})           # 持久化到配置文件
            └─► unset_network_proxy()                    # 关闭系统代理
  └─► 信号 task_over(biz_result) → GUI 更新显示 + 按钮变为"下一步"
```

#### 步骤二：抓取文章列表

```
GUI (MainWindow.step_two_btn_on_click)
  └─► GetArticleListThread.start(target_time=datetime)
       └─► ArticleListCrawler.start()
            └─► 开启系统代理 + mitmproxy
            └─► 用户在微信内访问历史消息页面
                 └─► ArticleListResponseHandler 捕获分页接口 flow (action=getmsg)
            └─► 获得模板 flow 后，跨线程调用重放：
                 get_article_list(offset, count)
                 └─► new_flow = template.copy()
                 └─► new_flow.request.query["offset"] = str(offset)
                 └─► master.commands.call("replay.client", [new_flow])
                 └─► 解析响应 JSON → general_msg_list → list[dict]
            └─► 循环分页：
                 parse_and_crop_article_list(articles, target_time, offset, count)
                 └─► 只保留目标月份内的文章
                 └─► 解析出 title / content_url / publishing_time / type / author
  └─► 信号 task_over(all_articles) → 弹窗确认 → 进入步骤三
```

#### 步骤三：文章内容爬取（含人机验证，三阶段流水线）

```
GUI (start_article_content_crawl)
  └─► GetArticleContentThread.start(article_list, to_calc_fee)
       └─► persist_articles_to_db(article_list)
            └─► session.add(Article(**article)) → session.commit() 写入 SQLite
       └─► 启动三阶段流水线（生产者-消费者队列解耦，最大化吞吐量）：

          ┌───────────────────────────────────────────────────────────┐
          │  Stage1：浏览器爬取（单线程，防反爬）                       │
          │  ContentCrawler.crawl_pages_for_pipeline()                │
          │    └─► 初始化 Playwright Chromium（headed，屏外隐藏）       │
          │    └─► 逐篇 page.goto(content_url)：                       │
          │         ┌─► 人机验证检测 + GUI交互（同旧逻辑）              │
          │         └─► 提取 crop_text, reader_stats                  │
          │    └─► 结果 {article_id, crop_text, reader_stats}         │
          │         推入 _raw_queue（原始页面数据队列）                 │
          └───────────────────────┬───────────────────────────────────┘
                                  │ raw_queue
                                  ▼
          ┌───────────────────────────────────────────────────────────┐
          │  Stage2：LLM 落款解析（LLM_PARSE_WORKERS 线程并行）         │
          │  _parse_worker()                                          │
          │    └─► parse_creator_list_by_llm(crop_text)               │
          │         └─► POST GLM API（首选 glm-4.7，失败降级 glm-5）   │
          │         └─► 从文末300字符提取连续成片落款                  │
          │    └─► 结果 {article_id, creator_list}                    │
          │         推入 _parsed_queue（待格式化队列）                 │
          └───────────────────────┬───────────────────────────────────┘
                                  │ parsed_queue
                                  ▼
          ┌───────────────────────────────────────────────────────────┐
          │  Stage3：LLM 结构化 + 入库（LLM_FORMAT_WORKERS 线程并行）   │
          │  _format_worker()                                         │
          │    └─► to_calc_fee=True 时：                               │
          │         format_creator_list_by_llm(creator_list)          │
          │         └─► GLM response_format=json_object               │
          │         └─► 输出 {"文": [".."], "排版": [".."], ...}       │
          │    └─► 更新数据库 Article：                                │
          │         view_count / heart_count / like_count             │
          │         share_count / collect_count                       │
          │         creators_list / formatted_creators_list           │
          └───────────────────────────────────────────────────────────┘

       └─► _progress_poller() 独立线程轮询三阶段计数器 → GUI 实时进度
  └─► 信号 task_over(bool) → GUI 加载表格展示
```

#### 步骤四：表格展示与 Excel 导出

```
GUI (set_article_confirm_table)
  └─► ArticleListViewModel 构建 QStandardItemModel
       └─► 列顺序：发布时间、标题、原创声明、内容链接、类型、参与人员、...、阅读量、点赞数、...
       └─► content_url 列绑定 HyperlinkDelegate：鼠标悬浮变色 + 点击打开 QDesktopServices
       └─► view_count 超过 10w 自动显示"10万+"
       └─► to_calc_fee=True 时附加"格式化参与人员"列（JSON 结构化）
  └─► export_to_file(folder_path, to_calc_fee)
       └─► openpyxl.Workbook 创建 Excel
       └─► 表头加粗 + 浅蓝底色
       └─► 所有单元格居中、自适应列宽（最小 20）
       └─► 保存为 作品清单_YYYYMMDDHHMMSS.xlsx
```

---

## 四、关键技术点详解

### 4.1 mitmproxy 抓包与重放机制

**文件**：`controllers/crawler.py:54-239`

mitmproxy 用于绕过微信复杂的签名机制。核心思路是**捕获一次合法请求作为模板，仅修改分页参数后重放**。

```python
# 1. 在子线程中启动 asyncio 事件循环，运行 DumpMaster
# 2. 通过自定义 Addon (MpBizResponseHandler / ArticleListResponseHandler) 捕获流量
# 3. 捕获到目标 flow 后，调用 copy() 生成新 flow，只修改 query 参数：
new_flow = template_flow.copy()
new_flow.request.query["offset"] = str(offset)
new_flow.request.query["count"] = str(count)
# 4. 跨线程提交到 mitmproxy 的重放命令：
master.commands.call("replay.client", [new_flow])
# 5. 轮询等待 new_flow.response 被填充，解析 JSON
```

**关键实现**：

- `Crawler._run_loop()` 在子线程中绑定事件循环，通过 `threading.Event` 与主线程同步
- `_replay_and_wait()` 以 100ms 间隔轮询响应，带超时保护
- 跨线程安全：使用 `asyncio.run_coroutine_threadsafe` 提交协程到 mitmproxy 所在事件循环

### 4.2 Windows 系统代理开关

**文件**：`controllers/proxy.py:17-41`

通过修改 Windows 注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings`：

```python
winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{host}:{port}")
# 通过 WinInet API 刷新使修改立即生效（无需重启浏览器）
ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
```

程序异常退出时，`小夏推送统计工具.py` 的 `finally` 块会调用 `unset_network_proxy()` 清理，避免用户系统代理残留。

### 4.3 Playwright 人机验证智能处理

**文件**：`controllers/content_crawler.py:207-224`（验证判定）、`controllers/content_crawler.py:255-392`（流水线爬取）

**核心思路**：默认后台静默模式，仅在检测到验证页时临时将窗口移至屏幕可见区域。

```python
# 启动时移至屏幕外坐标（不可见）
args=["--window-position=-32000,-32000", "--window-size=1280,720"]

# 检测到验证页时通过 CDP 协议移动窗口回可见区域
cdp_session.send("Browser.setWindowBounds", {
    "windowId": window_id,
    "bounds": {"left": 100, "top": 100, "width": 1280, "height": 800}
})

# 跨线程阻塞/唤醒：GUI 线程弹窗，爬虫线程阻塞在 threading.Event
# 信号槽采用 DirectConnection，保证 Event.set() 在 GUI 线程立即执行
signals.verify_done.connect(self._on_verify_done, Qt.ConnectionType.DirectConnection)
```

**验证页判定**（双保险）：

1. URL 正则匹配 `mp/wappoc_appmsgcaptcha`
2. 页面 body 文本关键词匹配："环境异常"、"前往验证"、"人机验证"、"安全校验"

### 4.4 SQLAlchemy 临时数据库策略

**文件**：`database/db.py:11-43`

```python
# 数据库路径位于系统临时目录
TEMP_PATH = Path(tempfile.gettempdir()) / "xiaoxia_contribution_statistic_tool"
TEMP_DB_PATH = TEMP_PATH / "temp_db.db"

# 每次初始化前删除旧文件，保证每次运行都是全新干净的数据库
if db_path.exists():
    db_path.unlink()
```

**Article 表字段**（`models/article_models.py:6-25`）：

- 基础字段：`id`, `title`, `author`, `publishing_time`, `content_url`, `type`
- 参与人员：`creators_list`（原始文本）, `formatted_creators_list`（JSON 结构化）
- 统计数据：`view_count`, `like_count`, `heart_count`, `share_count`, `collect_count`

### 4.5 LLM 双阶段落款解析

**文件**：`llm/llm_parse.py:95-225`

采用**两阶段调用**策略，确保准确性：


| 阶段     | 函数                         | 模型设置                                         | 作用                                                                                                |
| -------- | ---------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| 第一阶段 | `parse_creator_list_by_llm`  | `temperature=0.3`, `response_format=text`        | 从文章末尾 300 字符中精准提取"连续成片落款"，过滤正文/广告/导航                                     |
| 第二阶段 | `format_creator_list_by_llm` | `temperature=0.3`, `response_format=json_object` | 将"排版：张三、李四"等自然语言转换为`{"排版": ["张三", "李四"]}` 的结构化数据，过滤单位/责编/出品行 |

**容错机制**：

- 首选模型 `glm-4.7`，失败自动降级 `glm-5`
- JSON 输出兜底解析：自动剥离 Markdown 代码块标记
- 无落款时返回空字符串或空对象 `{}`，不编造信息

### 4.6 QThread 信号槽线程模型

**文件**：`controllers/threads.py:18-221`

```
GUI 线程 (MainWindow)                    工作线程 (QThread)
     │  signals: task_over, report_index      │
     │──────────────────────────────────────► │ 运行耗时操作
     │◄────────────────────────────────────── │ 完成后 emit 信号
     │                                        │
     │ 槽函数在 GUI 线程执行，安全操作 UI     │
```

三种工作线程：


| 线程类                    | 职责             | 发射信号                                                                                               |
| ------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------ |
| `GetMpBizThread`          | 获取公众号 BIZ   | `task_over(str)`                                                                                       |
| `GetArticleListThread`    | 分页获取文章列表 | `task_over(list)`, `flow_got(bool)`, `report_index(int)`                                               |
| `GetArticleContentThread` | 逐篇爬取文章内容 | `article_list_persist_ok()`, `need_user_verify()`, `task_over(bool)`, `report_progress(int, int, str)` |

### 4.7 UI 自定义绘制与交互

**文件**：`models/ui_models.py:127-175`（HyperlinkDelegate）

- 重写 `paint()`：链接文字加下划线 + 鼠标悬浮变色
- 重写 `editorEvent()`：鼠标左键点击释放时调用 `QDesktopServices.openUrl()`
- 通过 `ItemDataRole.UserRole` 存储真实 URL，`DisplayRole` 显示"点击访问"文案

**文件**：`ui/ui_components.py:22-269`（MainWindow）

- `FramelessWindowHint` + `WA_TranslucentBackground` 实现无边框半透明窗口
- 自定义拖动：`mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent` 检测 `title_bar.underMouse()`
- `QStackedWidget` 实现步骤流程切换（步骤一/二/三/结果页）

### 4.8 三阶段流水线并行架构（Stage1/2/3）

**文件**：`controllers/threads.py:150-490`（GetArticleContentThread）

为解决"浏览器爬取慢 + LLM 调用高延迟"的串联瓶颈，采用**生产者-消费者队列解耦**的三阶段流水线：

```
Stage1 浏览器(单线程) → _raw_queue → Stage2 LLM解析(多线程) → _parsed_queue → Stage3 LLM格式化+入库(多线程)
```


| 阶段                     | 线程数                      | 输入         | 输出                     | 瓶颈                   |
| ------------------------ | --------------------------- | ------------ | ------------------------ | ---------------------- |
| Stage1 浏览器爬取        | 1（防反爬）                 | article_list | crop_text + reader_stats | 微信反爬限速、人机等待 |
| Stage2 LLM 落款提取      | LLM_PARSE_WORKERS（默认3）  | crop_text    | creator_list 纯文本      | GLM API 网络延迟       |
| Stage3 LLM 结构化 + 入库 | LLM_FORMAT_WORKERS（默认2） | creator_list | JSON格式化 + DB写入      | GLM API + SQLite 写入  |

**关键实现**：

- `queue.Queue` 作为线程间安全数据通道，None 哨兵控制 Worker 优雅退出
- `_progress_poller` 独立线程每 300ms 轮询三个计数器，向 GUI 发射合成进度消息：`浏览器 N/总 · 作者解析 N/总 · 格式化入库 N/总 | [队列深度]`
- `_stop_flag` (threading.Event) 全局停止信号，被所有阶段循环检查
- Stage3 Worker 完成后 `join()` 两个队列，确保 100% 无遗漏后再 `emit(task_over)`

---

## 五、配置文件说明（xiaoxia_tool_config.ini）

程序首次启动时自动生成默认配置文件。可通过 `write_config({key: value})` / `del_config(key)` 动态修改。

```ini
listen_port=8082                          # mitmproxy 监听端口
max_article_count_per_request=10          # 每次分页请求文章数量
max_timeout_s=6                           # 接口最大超时秒数
max_retries=3                             # 最大重试次数
fetch_interval_s=2                        # 请求间隔秒数（避免被微信风控）

max_llm_retries=5                         # LLM 最大重试次数
llm_fetch_interval_s=0.5                  # LLM 请求间隔
glm_api_key=xxx                           # 智谱 API Key
glm_model=glm-4.7                         # 首选模型
glm_backup_model=glm-5                    # 备选降级模型

mp_id=MzA3OTM1MTIzNQ==                    # 已获取的公众号 BIZ（运行时写入）
```

加载入口：`constants/constants.py:28`（`dotenv.load_dotenv(CONFIG_FILE)`）

---

## 六、打包与发布流程（build.py）

**文件**：`build.py:9-80`（`_get_browser_dir_config` 浏览器目录智能探测 + `main` 打包主函数）

**当前版本**：FILE_VERSION / PRODUCT_VERSION = `0.2.1.0`

```bash
python build.py
# 底层执行（示意，以实际日志输出为准）：
python -m nuitka 小夏推送统计工具.py \
    --standalone \                      # 独立目录模式
    --windows-console-mode=disable \    # 无控制台窗口（取代旧版 --windows-disable-console）
    --enable-plugin=pyside6 \           # PySide6 资源自动打包
    --enable-plugin=playwright \        # Playwright 驱动自动打包
    --include-data-dir=<自动探测源目录>=ms-playwright \
                                        # 浏览器二进制：优先级 1) %LOCALAPPDATA%\ms-playwright
                                        #           降级 2) .dist\.local-browsers
    --file-version=0.2.1.0 \
    --product-version=0.2.1.0 \
    --product-name=Xiaoxia Contribution Statistic Tool \
    --copyright=ZajacHax 2026 \
    --deployment \                      # 部署优化
    --lto=auto \                        # 链接时优化
    --show-progress \
    --show-memory \
    --jobs=10 \                         # 并行编译
    --output-dir=./build
```

**浏览器目录智能探测逻辑**（解决"文件夹拷不完整"问题）：

1. **首选源**：`%LOCALAPPDATA%\ms-playwright`（系统 Playwright 安装目录，chromium-xxxx/chrome-win64 完整文件）
2. **降级源**：项目内 `.dist\.local-browsers`（历史构建产物，本地无 ms-playwright 时使用）
3. **目标目录**：打包产物根目录下 `ms-playwright/`，与 `content_crawler.py:_get_browser_root()` 中的 `PLAYWRIGHT_BROWSERS_PATH` 完全对应
4. **安全兜底**：两者都不存在时发出 warning，不强制中止打包（用户可手动拷入）

> ⚠️ **关键修复（v0.2.1.0）**：
>
> - 旧版 `BROWSER_DIR = ".dist\.local-browsers=playwright\driver\package\.local-browsers"` 目标路径是 Playwright 内部目录，而运行时实际读取的是 `{程序根目录}\ms-playwright`（见 `content_crawler.py:72-78`），导致**浏览器文件拷入错误位置 → 运行时找不到 chromium**。
> - 现统一目标目录为 `ms-playwright`，同时引入源目录探测，避免依赖单个绝对路径失效。

**输出目录**：`build/小夏推送统计工具.dist/`（可直接分发的独立程序目录，`小夏推送统计工具.exe` 位于根目录，`ms-playwright/` 并列存放）

---

## 七、操作步骤（对应用户使用流程）

1. **获取 BIZ**：启动工具 → 点击"开始获取" → 系统代理开启 → 在微信中访问公众号文章 → 工具自动捕获 `__biz` 参数 → 持久化到配置文件
2. **抓取文章列表**：选择目标年月 → 点击"开始获取" → 在微信中打开历史消息页触发流量 → mitmproxy 捕获分页接口模板 → 循环重放分页 → 按月份过滤 → 得到当月文章索引列表
3. **爬取文章内容**：弹窗确认后自动启动 Playwright → 逐篇访问文章链接 → 自动检测人机验证（弹窗提示用户完成） → 调用阅读量接口 + LLM 解析落款 → 写入数据库
4. **查看与导出**：结果表格展示（支持点击链接跳转原文） → 勾选"计算稿费"开启作者结构化 → 点击"导出文件"生成 Excel

---

## 八、日志与排错

- **文件日志**：`app.log`（普通格式，UTF-8 编码，位于程序根目录）
- **控制台日志**：彩色级别标识（DEBUG 青 / INFO 绿 / WARNING 黄 / ERROR 红 / CRITICAL 紫）
- **日志获取**：`from utils.logging import get_logger; logger = get_logger(__name__)`
- 各阶段操作均有详细 info 级日志，可用于追溯抓取失败原因

---

## 九、微信公众号接口说明（调试参考）


| 接口用途           | URL                                                                                                                            | 关键参数                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| 历史消息入口       | `https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}#wechat_redirect`                                              | `__biz`                                                         |
| 分页获取文章       | `https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz={biz}&f=json&offset={offset}&count={count}&is_ok=1&scene=124&...` | `__biz`, `offset`, `count`，需附带微信签名参数                  |
| 获取阅读/点赞/分享 | `https://mp.weixin.qq.com/mp/getappmsgext`                                                                                     | POST:`__biz`, `mid`, `idx`, `sn`, `appmsg_token`，需附带 Cookie |

**返回 JSON 结构示例**（文章列表）：

```json
{
  "ret": 0,
  "errmsg": "ok",
  "general_msg_list": "{\"list\":[{\"comm_msg_info\":{\"datetime\":1782069714,...},\"app_msg_ext_info\":{\"title\":\"...\",\"content_url\":\"...\",\"author\":\"...\",\"item_show_type\":\"0\"}}]}"
}
```

---

## 十、模块引用关系图

```
小夏推送统计工具.py (入口)
└─► ui/ui_components.py (MainWindow)
    ├─► ui/ui_helper.py (表格样式)
    │   └─► models/ui_models.py (ViewModel + Delegate)
    │       ├─► helpers/helpers.py (get_article_list_from_db)
    │       │   └─► database/db.py (Session)
    │       │       └─► models/article_models.py + models/base_model.py
    │       └─► utils/format.py
    │
    ├─► controllers/threads.py (三大 QThread)
    │   ├─► controllers/crawler.py (MpBizCrawler + ArticleListCrawler)
    │   │   └─► controllers/proxy.py (系统代理开关)
    │   ├─► controllers/content_crawler.py (ContentCrawler)
    │   │   ├─► llm/llm_parse.py (GLM 调用)
    │   │   │   └─► constants/constants.py (API Key)
    │   │   └─► helpers/helpers.py (get_reader_stats)
    │   └─► helpers/helpers.py (parse_and_crop_article_list, persist_articles_to_db)
    │
    ├─► controllers/export.py (Excel 导出)
    │   └─► models/ui_models.py
    │
    └─► helpers/config_helper.py (读写配置)
        └─► constants/constants.py (CONFIG_FILE)
            └─► dotenv

exceptions/exceptions.py  （自定义异常，被 threads / content_crawler 引用）
utils/logging.py          （全局日志，被所有模块引用）
```

---

## 十一、关键设计决策记录


| 决策                                                       | 原因与权衡                                                                                                                                                                                                       |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **mitmproxy 重放而非直接构造请求**                         | 微信分页接口有复杂签名机制，直接构造请求易被拦截。通过捕获合法请求再修改分页参数，完全绕过签名问题                                                                                                               |
| **Playwright 默认 headed + 窗口移至屏幕外**                | 无头模式下更容易触发微信反爬；headed 且窗口移至屏幕外兼顾"用户无感"与"会话完整性"                                                                                                                                |
| **SQLite 临时文件数据库（每次启动重建）**                  | 工具属于单次运行性质，不需要长期历史；简化部署与清理；避免用户数据泄露风险                                                                                                                                       |
| **两阶段 LLM 调用（提取→结构化）**                        | 单阶段让 LLM 直接输出 JSON 会有"混入正文"风险；分两步：先准确提取范围，再做字段拆分，显著提升精度                                                                                                                |
| **三阶段流水线 + 队列解耦（Stage1/2/3）**                  | 浏览器爬取（单线程防反爬）和 LLM API 调用（高延迟 IO 密集）是瓶颈差异极大的两个阶段；用队列解耦后 Stage2/Stage3 可多线程并行，整体吞吐量提升约 2~3 倍                                                            |
| **QThread + 信号槽实现异步**                               | 避免阻塞 GUI；Qt 信号槽天然线程安全；人机验证场景需"爬虫阻塞→GUI提示→用户操作→爬虫唤醒"的线程协作                                                                                                             |
| **Windows 注册表方式控制系统代理**                         | 微信 PC 客户端读取系统代理；mitmproxy 通过全局代理捕获流量；退出时必须还原否则影响用户正常上网                                                                                                                   |
| **Nuitka standalone 模式打包**                             | Playwright 浏览器资源 + PySide6 Qt 资源体积大，但避免用户安装 Python；使用`--enable-plugin` 自动处理资源依赖                                                                                                     |
| **打包时浏览器目录智能探测 + 目标统一为 `ms-playwright/`** | 旧版`=playwright\driver\package\.local-browsers` 目标路径与运行时 `PLAYWRIGHT_BROWSERS_PATH` 不一致，导致 chromium 找不到；同时 `%LOCALAPPDATA%` 绝对路径在不同机器失效，故引入两级降级探测 + 目标路径对齐运行时 |
