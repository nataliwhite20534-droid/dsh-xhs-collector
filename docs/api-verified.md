# API 验证记录

> 本文档记录了 `cn-scraper-mcp 0.5.0` 的源码级验证过程。

## 验证时间

2026-09-03

## 验证方法

1. 从 PyPI 下载源码包：
   `pip download cn-scraper-mcp==0.5.0`
2. 解压 tarball，读取源码文件
3. 对比 README 中的代码示例与源码中的真实实现

## 关键发现

### ❌ README 早期版本的错误

| 错误 | 说明 |
|------|------|
| 类名 `XHSCollector` | 源码中不存在此名称 |
| 方法 `search_batch()` | 源码中是 `search(keyword, limit)` |
| 字段 `note_url` | 源码中真实字段是 `href` |
| 字段 `date` | 搜索结果中无日期字段 |

### ✅ 真实 API

**包**：`cn-scraper-mcp 0.5.0`（PyPI verified, 源码 2.6MB）

**入口**：`from cn_scraper_mcp import XiaohongshuEngine`

**源码路径**：

```
cn_scraper_mcp-0.5.0/src/cn_scraper_mcp/engines/xiaohongshu.py
  class XiaohongshuEngine
  ├── __init__(cookies_path, port=9222)
  ├── ensure_browser()
  ├── search(keyword, limit=10) → dict
  ├── _parse_search()
  ├── get_note(note_id, xsec_token=None) → dict
  ├── get_comments(note_id, xsec_token=None) → dict
  └── cleanup()
```

**search() 返回结构**：

```python
{
    "keyword": str,          # 搜索关键词
    "state": str,            # "success" | "limited" | "error"
    "count": int,            # 实际返回的条数
    "items": [
        {
            "title": str,
            "author": str,
            "likes": int,       # 标准化后的点赞数
            "noteId": str,      # 全局去重用
            "href": str,        # 完整小红书 URL
            "xsec_token": str,  # 有时效，24h 内
        }
    ],
    "error_code": str | None,
    "error_message": str | None,
}
```

**错误码说明**：

| error_code | 含义 | 处理 |
|------------|------|------|
| XHS_BROWSER_UNAVAILABLE | 无法启动浏览器 | 检查 Chrome/Obscura 安装 |
| XHS_COOKIE_EXPIRED | Cookie 过期 | 重新扫码登录 |
| XHS_RATE_LIMITED | IP 被限流 | 降低请求频率或换 IP |
| None | 成功 | — |

## 下一步验证

- [ ] 在真实环境运行 `engine.search("完美日记", 10)`
- [ ] 验证 Cookie 刷新机制
- [ ] 测试 `get_note()` 能否获取笔记正文
- [ ] 测试 `get_comments()` 是否返回评论