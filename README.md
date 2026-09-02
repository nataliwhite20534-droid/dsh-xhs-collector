# dsh-xhs-collector

> 一键批量抓取小红书搜索结果，让 AI Agent 在住宅 IP 环境下稳定获取数据。

## 这是什么

在 [DSH (DeepSeek Harness)](https://github.com/deepseek-ai/deepseek-harness) 中调用 `cn-scraper-mcp` 的 XHS 引擎，
通过本地 Chrome CDP（`--remote-debugging-port=9251`）执行搜索并解析结果。
配合 `guided_login()` 自动收割 Cookie，整条链路可在 3 分钟内跑通。

## 核心特性

- **批量搜索**：一次传多个关键词，输出统一 JSON
- **真实数据**：绕过反爬机制（CDP + 真实 Chrome 指纹）
- **去重友好**：同关键词去重、跨关键词去重
- **结构化输出**：每条帖子含 title/author/likes/noteId/xsec_token

## 安装

```bash
pip install cn-scraper-mcp>=0.5.0
```

## 一键登录（仅首次）

```python
from cn_scraper_mcp.cookie_harvest import guided_login
result = guided_login("xiaohongshu", port=9251, timeout=120)
print(result)  # {platform: "xiaohongshu", count: 11, status: "ok"}
```

Chrome 窗口会弹出，扫码后 Cookie 自动保存到 `~/.cn-scraper-cookies/xiaohongshu.json`。

## 使用

### 单次搜索

```python
from cn_scraper_mcp.engines.xiaohongshu import XiaohongshuEngine

engine = XiaohongshuEngine()
result = engine.search("桂林家教", limit=10)

for item in result["items"]:
    print(f"{item['title']} | {item['author']} | likes={item['likes']}")
    print(f"  {item['href']}")
```

### 批量（CLI）

```bash
# keywords.txt（每行一个）
echo "桂林家教" > keywords.txt
echo "桂林大学生家教" >> keywords.txt
echo "桂林英语家教" >> keywords.txt

python xhs-batch-search.py --file keywords.txt --limit 10 --out result.json --delay 2
```

输出示例：

```json
{
  "queries": [{"keyword": "桂林家教", "limit": 10}],
  "results": [{
    "keyword": "桂林家教",
    "state": "ok",
    "count": 10,
    "items": [
      {
        "title": "揭秘！2026桂林一对一伴读价格📝",
        "author": "家教114大学生兼职平台",
        "likes": "8",
        "noteId": "6a3a01bc00000000",
        "xsec_token": "ABws0wj-BzanGzpz2SqE6aOzGHmPupVyEOPGHyKwzPvUA=",
        "url": "https://www.xiaohongshu.com/search_result/..."
      }
    ]
  }]
}
```

## 已知问题与修复

### `_detect_page_state` 误判 login_expired

**症状**：搜索能跑出数据，但返回 `state="login_expired"`。

**根因**：`cn_scraper_mcp/engines/xiaohongshu.py` 的 `_detect_page_state()` 用 `if '登录' in page_text` 判断，
会误匹配页脚版权信息中的"登录"关键词（如"互联网举报中心"）。

**修复**：将判断顺序改为「item_count > 0 → 直接返回 ok」。

```python
# Before:
if '登录' in page_text:
    return ('login_expired', ...)

# After:
if item_count > 0:
    return ('ok', None, None)  # 有 items 就是正常的搜索结果
if '登录' in page_text:
    return ('login_expired', ...)
```

## 工作原理

```
用户调用 search()
   ↓
1. ensure_browser() 启动 Chrome with --remote-debugging-port=9251
   ↓
2. _inject_cookies() 通过 CDP Network.setCookie 注入 XHS cookies
   ↓
3. CDPClient.evaluate() 执行 SEARCH_EXTRACTOR JS 提取 DOM
   ↓
4. _parse_search() 解析 items、检测 page state（ip_risk/login_expired/ok）
   ↓
5. 返回结构化结果
```

## 限制与警告

- **XHS 强反爬**：仅在住宅 IP/本地网络下有效。数据中心 IP 必封（error_code=300012）。
- **Cookie 有期**：web_session 过期需要重新 guided_login。
- **抓取频率**：单次 2s 间隔，连续 10+ 次可能触发滑块验证。
- **合规使用**：仅用于学习研究，遵守小红书用户协议。

## 关联项目

- [cn-scraper-mcp](https://github.com/goesByhc/cn-scraper-mcp) — 底层 MCP 引擎
- [jackwener/xiaohongshu-cli](https://github.com/jackwener/xiaohongshu-cli) — 备用 XHS 工具
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) — 运行平台

## 许可证

MIT — 详见 [LICENSE](LICENSE)