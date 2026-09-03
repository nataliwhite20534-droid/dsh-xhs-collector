ï»¿# dsh-xhs-collector

> ä¸é®æ¹éæåå°çº¢ä¹¦æç´¢ç»æï¼è®© AI Agent å¨ä½å® IP ç¯å¢ä¸ç¨³å®è·åæ°æ®ã

## è¿æ¯ä»ä¹

å¨ [DSH (DeepSeek Harness)](https://github.com/deepseek-ai/deepseek-harness) ä¸­è°ç¨ `cn-scraper-mcp` ç XHS å¼æï¼
éè¿æ¬å° Chrome CDPï¼`--remote-debugging-port=9251`ï¼æ§è¡æç´¢å¹¶è§£æç»æã
éå `guided_login()` èªå¨æ¶å² Cookieï¼æ´æ¡é¾è·¯å¯å¨ 3 åéåè·éã

## æ ¸å¿ç¹æ§

- **æ¹éæç´¢**ï¼ä¸æ¬¡ä¼ å¤ä¸ªå³é®è¯ï¼è¾åºç»ä¸ JSON
- **çå®æ°æ®**ï¼ç»è¿åç¬æºå¶ï¼CDP + çå® Chrome æçº¹ï¼
- **å»éåå¥½**ï¼åå³é®è¯å»éãè·¨å³é®è¯å»é
- **ç»æåè¾åº**ï¼æ¯æ¡å¸å­å« title/author/likes/noteId/xsec_token

## å®è£

```bash
pip install cn-scraper-mcp>=0.5.0
```

## ä¸é®ç»å½ï¼ä»é¦æ¬¡ï¼

```python
from cn_scraper_mcp.cookie_harvest import guided_login
result = guided_login("xiaohongshu", port=9251, timeout=120)
print(result)  # {platform: "xiaohongshu", count: 11, status: "ok"}
```

Chrome çªå£ä¼å¼¹åºï¼æ«ç å Cookie èªå¨ä¿å­å° `~/.cn-scraper-cookies/xiaohongshu.json`ã

## ä½¿ç¨

### åæ¬¡æç´¢

```python
from cn_scraper_mcp.engines.xiaohongshu import XiaohongshuEngine

engine = XiaohongshuEngine()
result = engine.search("æ¡æå®¶æ", limit=10)

for item in result["items"]:
    print(f"{item['title']} | {item['author']} | likes={item['likes']}")
    print(f"  {item['href']}")
```

### æ¹éï¼CLIï¼

```bash
# keywords.txtï¼æ¯è¡ä¸ä¸ªï¼
echo "æ¡æå®¶æ" > keywords.txt
echo "æ¡æå¤§å­¦çå®¶æ" >> keywords.txt
echo "æ¡æè±è¯­å®¶æ" >> keywords.txt

python xhs-batch-search.py --file keywords.txt --limit 10 --out result.json --delay 2
```

è¾åºç¤ºä¾ï¼

```json
{
  "queries": [{"keyword": "æ¡æå®¶æ", "limit": 10}],
  "results": [{
    "keyword": "æ¡æå®¶æ",
    "state": "ok",
    "count": 10,
    "items": [
      {
        "title": "æ­ç§ï¼2026æ¡æä¸å¯¹ä¸ä¼´è¯»ä»·æ ¼ð",
        "author": "å®¶æ114å¤§å­¦çå¼èå¹³å°",
        "likes": "8",
        "noteId": "6a3a01bc00000000",
        "xsec_token": "ABws0wj-BzanGzpz2SqE6aOzGHmPupVyEOPGHyKwzPvUA=",
        "url": "https://www.xiaohongshu.com/search_result/..."
      }
    ]
  }]
}
```

## å·²ç¥é®é¢ä¸ä¿®å¤

### `_detect_page_state` è¯¯å¤ login_expired

**çç¶**ï¼æç´¢è½è·åºæ°æ®ï¼ä½è¿å `state="login_expired"`ã

**æ ¹å **ï¼`cn_scraper_mcp/engines/xiaohongshu.py` ç `_detect_page_state()` ç¨ `if 'ç»å½' in page_text` å¤æ­ï¼
ä¼è¯¯å¹éé¡µèçæä¿¡æ¯ä¸­ç"ç»å½"å³é®è¯ï¼å¦"äºèç½ä¸¾æ¥ä¸­å¿"ï¼ã

**ä¿®å¤**ï¼å°å¤æ­é¡ºåºæ¹ä¸ºãitem_count > 0 â ç´æ¥è¿å okãã

```python
# Before:
if 'ç»å½' in page_text:
    return ('login_expired', ...)

# After:
if item_count > 0:
    return ('ok', None, None)  # æ items å°±æ¯æ­£å¸¸çæç´¢ç»æ
if 'ç»å½' in page_text:
    return ('login_expired', ...)
```

## å·¥ä½åç

```
ç¨æ·è°ç¨ search()
   â
1. ensure_browser() å¯å¨ Chrome with --remote-debugging-port=9251
   â
2. _inject_cookies() éè¿ CDP Network.setCookie æ³¨å¥ XHS cookies
   â
3. CDPClient.evaluate() æ§è¡ SEARCH_EXTRACTOR JS æå DOM
   â
4. _parse_search() è§£æ itemsãæ£æµ page stateï¼ip_risk/login_expired/okï¼
   â
5. è¿åç»æåç»æ
```

## éå¶ä¸è­¦å

- **XHS å¼ºåç¬**ï¼ä»å¨ä½å® IP/æ¬å°ç½ç»ä¸ææãæ°æ®ä¸­å¿ IP å¿å°ï¼error_code=300012ï¼ã
- **Cookie ææ**ï¼web_session è¿æéè¦éæ° guided_loginã
- **æåé¢ç**ï¼åæ¬¡ 2s é´éï¼è¿ç»­ 10+ æ¬¡å¯è½è§¦åæ»åéªè¯ã
- **åè§ä½¿ç¨**ï¼ä»ç¨äºå­¦ä¹ ç ç©¶ï¼éµå®å°çº¢ä¹¦ç¨æ·åè®®ã

## å³èé¡¹ç®

- [cn-scraper-mcp](https://github.com/goesByhc/cn-scraper-mcp) â åºå± MCP å¼æ
- [jackwener/xiaohongshu-cli](https://github.com/jackwener/xiaohongshu-cli) â å¤ç¨ XHS å·¥å·
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) â è¿è¡å¹³å°

## è®¸å¯è¯

MIT â è¯¦è§ [LICENSE](LICENSE)\n

---

## ð DSH çææå

æ¬é¡¹ç®æ¯ **DSH (DeepSeek Harness)** çæçä¸åï¼åç³»åè¿æï¼

- ð [`dsh-moe-plugin`](https://github.com/nataliwhite20534-droid/dsh-moe-plugin) â èå±æ§ Persona ç³»ç»ï¼10 ç§é¢è®¾å¡çï¼
- âï¸ [`dsh-4-role-workflow`](https://github.com/nataliwhite20534-droid/dsh-4-role-workflow) â 4 è§è² Agent å·¥ä½æµ
- ð [`dsh-china-research-notes`](https://github.com/nataliwhite20534-droid/dsh-china-research-notes) â ä¸­å½å¹³å°åç¬å®æç¬è®°

> æ¬¢è¿ Star / Fork / Issueï¼æ³åä¸å¼åï¼Fork åæ PR å³å¯ã

## ð ç¸å³é¾æ¥

- [DSH (DeepSeek Harness) ä¸»ä»](https://github.com/deepseek-ai/deepseek-harness)

---

## 🌏 DSH 生态成员

本项目是 **DSH (DeepSeek Harness)** 生态的一员，同系列还有：

- 🎀 `dsh-moe-plugin` — 萌属性 Persona 系统（10 种预设卡片）
- ⚙️ `dsh-4-role-workflow` — 4 角色 Agent 工作流
- 📓 `dsh-china-research-notes` — 中国平台反爬实战笔记

> 欢迎 Star / Fork / Issue！想参与开发？Fork 后提 PR 即可。

## 🔗 相关链接

- [DSH (DeepSeek Harness) 主仓](https://github.com/deepseek-ai/deepseek-harness)
