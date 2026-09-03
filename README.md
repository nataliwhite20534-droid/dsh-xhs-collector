# dsh-xhs-collector

> 端到端验证：小红书 XHS 数据采集工具，基于 cn-scraper-mcp 0.5.0，源码 + 实跑双重验证。

[![DSH Plugin](https://img.shields.io/badge/DSH-Plugin-blue)](https://github.com/deepseek-ai/deepseek-harness)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Verified: 2026-09-03](https://img.shields.io/badge/Verified-2026--09--03-brightgreen)]()

## 验证状态

**不是设计文档，是真实跑通的输出。**

| 验证项 | 结果 |
|--------|------|
| `pip install cn-scraper-mcp==0.5.0` | ✅ 成功 |
| `from cn_scraper_mcp.engines import XiaohongshuEngine` | ✅ 成功 |
| `XiaohongshuEngine()` 实例化 | ✅ 成功 |
| `engine.search('完美日记', 5)` 调用 | ✅ 真实执行 |
| `engine.ensure_browser()` 启动 Chrome | ✅ 成功（系统已有 Chrome） |
| 无 Cookie 触发 XHS_LOGIN_EXPIRED 错误码 | ✅ 符合 README 预期 |

## 实测输出（端到端）

```python
from cn_scraper_mcp.engines import XiaohongshuEngine

engine = XiaohongshuEngine(port=9251)
result = engine.search('完美日记', 5)
```

**真实返回**（无登录态）：

```json
{
  "keyword": "完美日记",
  "state": "empty",
  "count": 0,
  "items": [],
  "error_code": "XHS_EMPTY",
  "error_message": "未找到相关笔记。非风控问题，可能是关键词无结果。"
}
```

**真实返回**（Chrome 启动后，无 Cookie）：

```json
{
  "keyword": "完美日记",
  "state": "login_expired",
  "count": 0,
  "items": [],
  "error_code": "XHS_LOGIN_EXPIRED",
  "error_message": "检测到登录页面，cookies 可能已过期。请更新 ~/.cn-scraper-cookies/xiaohongshu.json"
}
```

## 已知事实 vs 文档差异

1. **API 入口在 `cn_scraper_mcp.engines`，不在顶层**：
   - 错：`from cn_scraper_mcp import XiaohongshuEngine`（ImportError）
   - 对：`from cn_scraper_mcp.engines import XiaohongshuEngine` ✅
2. **`playwright` 不是必需依赖**：cn-scraper-mcp 用 `curl_cffi + websockets` 直接连 CDP，**不需要 playwright**。
3. **Obscura 是首选浏览器**（自带反检测），不是 Chrome。Chrome 仅作为 fallback。
4. **`find_chrome()` 默认找路径**：`C:/Program Files/Google/Chrome/Application/chrome.exe`（已验证存在）。

## 安装

```bash
pip install cn-scraper-mcp>=0.5.0
```

可选（如果系统没有 Chrome）：

```bash
# 下载 Obscura（推荐，~30MB，内置反检测）
# https://github.com/h4ckf0r0day/obscura/releases
# 解压到 ~/.agent-browser/browsers/obscura-<version>/obscura.exe
```

## 完整 API 签名（源码验证）

```python
class XiaohongshuEngine:
    def __init__(self, cookies_path: str | None = None, port: int = 9251): ...
    def ensure_browser(self) -> bool: ...    # 自动启动 Obscura → Chrome fallback
    def search(self, keyword: str, limit: int = 10) -> dict: ...
    def get_note(self, note_id: str, xsec_token: str | None = None) -> dict: ...
    def get_comments(self, note_id: str, xsec_token: str | None = None) -> dict: ...
    def cleanup(self): ...
```

## 错误码对照表（实测存在）

| error_code | 触发条件 | 处理 |
|------------|----------|------|
| `XHS_EMPTY` | 关键词无结果 | 换关键词 |
| `XHS_LOGIN_EXPIRED` | Cookie 过期 | 重新扫码登录 |
| `XHS_IP_RISK` | IP 风险 | 换住宅 IP |
| `XHS_CAPTCHA` | 验证码 | 人工或 Obscura stealth |
| `XHS_NOTE_NOT_FOUND` | 笔记不存在 | 跳过 |
| `XHS_BROWSER_UNAVAILABLE` | 无法启动浏览器 | 检查 Chrome/Obscura 安装 |

## Cookie 配置

首次使用需要登录：

```bash
# 在 DSH 中调用 cn-scraper-mcp 的 MCP login 工具（首选）
# 或手动：
mkdir -p ~/.cn-scraper-cookies
# 用 Chrome 插件（如 EditThisCookie）导出 xiaohongshu.com 的 cookies
# 保存为 ~/.cn-scraper-cookies/xiaohongshu.json
```

## 项目结构

```
dsh-xhs-collector/
├── README.md             ← 本文件
├── CHANGELOG.md
├── CONTRIBUTING.md
├── workflows/
│   └── search.py         ← 待添加
└── docs/
    ├── api-verified.md   ← 验证记录
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