# 小夏贡献统计工具

## 技术栈：

- Python 3.12
- 包管理：uv
- 编译：Nuitka

## 详细模块：

- 用户界面：PySide 6 + QTDesigner (界面设计)
- 数据库：SQLite + PyMySQL (数据库引擎) + SQLAlchemy (ORM框架)
- 抓包：

## 基础配置

biz链接 https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzA3OTM1MTIzNQ==#wechat_redirect

## 操作步骤：

1. 获取公众号biz，获取方法：浏览器任意打开一篇本公众号的文章（不能是图文），按F12键打开开发人员工具，按ctrl+f，搜索“biz”，找到第一个搜索结果，类似于`biz: "MzA3OTM1MTIzNQ==" || ""`，第一个引号内的内容即为本公众号的biz，如`MzA3OTM1MTIzNQ==`。将biz复制下来。
2. 构造公众号“历史消息”链接，返回给用户，用户在微信内打开该链接