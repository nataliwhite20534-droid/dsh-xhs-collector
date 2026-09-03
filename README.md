# dsh-xhs-collector

> 小红书 XHS 数据采集工具，基于 `cn-scraper-mcp` 0.5.0，
> 源码 + 实跑双重验证，错误码对照表完备。

[![DSH Plugin](https://img.shields.io/badge/DSH-Plugin-blue)](https://github.com/deepseek-ai/deepseek-harness)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Verified: 2026-09-03](https://img.shields.io/badge/Verified-2026--09--03-brightgreen)]()

## 验证状态

**不是设计文档，是真实跑通的输出。**

| 验证项 | 结果 |
|--------|------|
| \`pip install cn-scraper-mcp==0.5.0\` | ✅ 成功 |
| \`from cn_scraper_mcp.engines import XiaohongshuEngine\` | ✅ 成功 |
| \`XiaohongshuEngine()\` 实例化 | ✅ 成功 |
| \`engine.search('完美日记', 5)\` 调用 | ✅ 真实执行 |
| \`engine.ensure_browser()\` 启动 Chrome | ✅ 成功（系统已有 Chrome） |
| 无 Cookie 触发 XHS_LOGIN_EXPIRED 错误码 | ✅ 符合预期 |

## 真实返回（端到端）

```python
from cn_scraper_mcp.engines import XiaohongshuEngine

engine = XiaohongshuEngine(port=9251)
result = engine.search('完美日记', 5)
```

**无登录态返回**（关键词无结果）：

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

**Chrome 启动后，无 Cookie 返回**：

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

| 误区 | 正确做法 |
|------|----------|
| \`from cn_scraper_mcp import XiaohongshuEngine\` | \`from cn_scraper_mcp.engines import XiaohongshuEngine\` ✅ |
| 必须装 playwright | 不需要，cn-scraper-mcp 用 curl_cffi + CDP 直接连 |
| 用 Chrome | Obscura 首选（内置反检测），Chrome 作为 fallback |

## 安装

```bash
pip install cn-scraper-mcp>=0.5.0
```

## 完整 API 签名（源码验证）

```python
class XiaohongshuEngine:
    def __init__(self, cookies_path: str | None = None, port: int = 9251): ...
    def ensure_browser(self) -> bool: ...    # Obscura → Chrome fallback
    def search(self, keyword: str, limit: int = 10) -> dict: ...
    def get_note(self, note_id: str, xsec_token: str | None = None) -> dict: ...
    def get_comments(self, note_id: str, xsec_token: str | None = None) -> dict: ...
    def cleanup(self): ...
```

## 错误码对照表

| error_code | 触发条件 | 处理 |
|-------------|----------|------|
| \`XHS_EMPTY\` | 关键词无结果 | 换关键词 |
| \`XHS_LOGIN_EXPIRED\` | Cookie 过期 | 重新扫码登录 |
| \`XHS_IP_RISK\` | IP 风险 | 换住宅 IP |
| \`XHS_CAPTCHA\` | 验证码 | 人工或 Obscura stealth |
| \`XHS_NOTE_NOT_FOUND\` | 笔记不存在 | 跳过 |
| \`XHS_BROWSER_UNAVAILABLE\` | 无法启动浏览器 | 检查 Chrome/Obscura 安装 |

## Cookie 配置

首次使用需要登录：

```bash
# 在 DSH 中调用 cn-scraper-mcp 的 guided_login
# 或手动配置：
mkdir -p ~/.cn-scraper-cookies
# 放入 xiaohongshu.json（格式见 cn-scraper-mcp 文档）
```

## 配套工具

- [dsh-4-role-workflow](../dsh-4-role-workflow) — 4 角色协作工作流（用 xhs-cli）
- [dsh-china-research-notes](../dsh-china-research-notes) — 中国平台踩坑经验合集