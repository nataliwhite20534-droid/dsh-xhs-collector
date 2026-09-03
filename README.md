# dsh-xhs-collector

> 在住宅 IP 环境下稳定抓取小红书数据，为 AI 决策提供真实口碑依据。

[![DSH Plugin](https://img.shields.io/badge/DSH-Plugin-blue)](https://github.com/deepseek-ai/deepseek-harness)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**核心依赖**：[cn-scraper-mcp](https://pypi.org/project/cn-scraper-mcp/) `0.5.0`（真实存在，源码已解压验证）

## 已知问题

> ⚠️ **README 早期版本曾错误地将 `XiaohongshuEngine` 写成 `XHSCollector`。**
> 以下是经过源码验证的准确 API，代码示例全部可运行。

## 工作原理

```
关键词搜索请求
     ↓
CDP 真实 Chrome（住宅 IP 出口）
     ↓
Cookie 自动刷新（每 30 分钟）
     ↓
JS 提取页面数据 → 标准化 JSON
     ↓
→ DSH Agent / 人工分析师 / BI 工具
```

## 安装

```bash
pip install cn-scraper-mcp>=0.5.0 playwright
playwright install chromium
# 推荐安装 Obscura（内置反检测）
pip install obscura
```

## 真实 API（源码验证）

### 类：XiaohongshuEngine

```python
from cn_scraper_mcp import XiaohongshuEngine

engine = XiaohongshuEngine(
    cookies_path="~/.cn-scraper-cookies/xiaohongshu.json",
    port=9222,   # Chrome 远程调试端口
)
```

### 方法 1：search(keyword, limit=10)

```python
result = engine.search("完美日记", limit=50)
print(result)
# {
#   "keyword": "完美日记",
#   "state": "success",  # 或 "limited"/"error"
#   "count": 50,
#   "items": [
#     {
#       "title": "完美日记九色眼影盘真人试色",
#       "author": "皮皮不会化妆",
#       "likes": 2847,
#       "noteId": "67a8f2c3000000001e02f5e",
#       "href": "https://www.xiaohongshu.com/discovery/item/67a8f2c3...",
#       "xsec_token": "..."
#     },
#   ],
#   "error_code": None,
#   "error_message": None
# }
```

### 方法 2：get_note(note_id, xsec_token=None)

```python
note = engine.get_note(
    note_id="67a8f2c3000000001e02f5e",
    xsec_token="...",
)
# 返回笔记正文 + 图片列表
```

### 方法 3：get_comments(note_id, xsec_token=None)

```python
comments = engine.get_comments(
    note_id="67a8f2c3000000001e02f5e",
    xsec_token="...",
)
# 返回评论列表
```

## 批量搜索（完整示例）

```python
from cn_scraper_mcp import XiaohongshuEngine
import json, time

engine = XiaohongshuEngine()
keywords = ["完美日记", "完美日记眼影", "完美日记测评", "完美日记推荐"]

all_items = []
for kw in keywords:
    r = engine.search(kw, limit=100)
    print(f"[{kw}] {r['state']} → {r['count']} 条")
    all_items.extend(r['items'])
    time.sleep(5)  # 防风控

# 全局去重
seen = set()
deduped = []
for item in all_items:
    if item['noteId'] not in seen:
        seen.add(item['noteId'])
        deduped.append(item)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump({"total": len(deduped), "items": deduped}, f, ensure_ascii=False, indent=2)

print(f"采集完成，共 {len(deduped)} 条去重笔记")
```

## 输出字段（真实字段）

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 笔记标题 |
| author | string | 作者昵称 |
| likes | int | 点赞数（标准化后） |
| noteId | string | 笔记唯一 ID（去重用） |
| href | string | 笔记完整 URL |
| xsec_token | string | 防盗链 token（有实效） |
| state | string | success / limited / error |
| error_code | string | 错误码或 None |
| error_message | string | 错误描述或 None |

## Cookie 配置

首次使用需要扫码登录：

```bash
# 方法 1：用 MCP server 的 guided login
# 在 DSH 中调用 cn-scraper-mcp 的 MCP 工具 login

# 方法 2：手动放入文件
mkdir -p ~/.cn-scraper-cookies
# 把浏览器 cookie 导出为 JSON（Chrome 插件：EditThisCookie）
# 放入 ~/.cn-scraper-cookies/xiaohongshu.json
```

## 已知限制

| 限制 | 说明 | 应对 |
|------|------|------|
| 数据中心 IP 被封 | 必须用住宅 IP | 用 Obscura 或真实代理 |
| xsec_token 时效 | 链接 token 通常 24h 内失效 | 采集时同步抓正文 |
| 搜索结果上限 | 非登录用户有限流 | 登录 Cookie 效果更好 |
| Python >= 3.11 | cn-scraper-mcp 要求 | 检查 `python --version` |

## 项目结构

```
dsh-xhs-collector/
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── workflows/
│   └── search.py
└── docs/
    ├── api-verified.md    ← 源码验证过的 API 说明
    ├── case-study.md
    └── troubleshooting.md
```

## 真实案例

📊 [完美日记 30 天口碑数据采集](./docs/case-study.md)

## 🌏 DSH 生态

- 🎀 [`dsh-moe-plugin`](https://github.com/nataliwhite20534-droid/dsh-moe-plugin) — 萌属性 Persona 系统
- ⚙️ [`dsh-4-role-workflow`](https://github.com/nataliwhite20534-droid/dsh-4-role-workflow) — 4 角色 Agent 工作流
- 📓 [`dsh-china-research-notes`](https://github.com/nataliwhite20534-droid/dsh-china-research-notes) — 中国平台反爬实战笔记

## 免责声明

本工具仅供学习和研究使用。请遵守小红书《用户协议》和相关法律法规，
不要大规模爬取或用于商业牟利。数据采集者自行承担使用风险。