# 常见问题排查

## 1. 弹出验证码（滑动验证）

**症状**：Chrome 窗口弹出小红书滑块验证码

**原因**：IP 被识别为非住宅 IP，或请求频率过高

**解决方案**：

```python
# 方案 A：更换代理
collector = XHSCollector(
    proxy="http://username:password@proxy.example.com:8080",
)

# 方案 B：降低并发
collector.search_batch(keywords=[...], max_concurrent=1)

# 方案 C：延长请求间隔
collector.search_batch(keywords=[...], delay_between=5.0)  # 秒
```

## 2. Cookie 过期

**症状**：返回结果为空，或返回 401 错误

**解决方案**：

```bash
python -c "from cn_scraper import XHSCollector; XHSCollector().guided_login()"
```

## 3. 搜索结果少于预期

**症状**：某些关键词只返回几十条

**原因**：
- 非登录用户搜索结果上限约 1000 条/关键词
- 平台去重了部分相似内容

**解决方案**：
- 换更多细分关键词（品类词 + 场景词）
- 登录状态下采集（cookie 有效时效果更好）

## 4. playwright 找不到 chromium

**症状**：`playwright._impl.api_errors.Error: Executable doesn't exist`

**解决方案**：

```bash
playwright install chromium
# 如果是 Windows 且装在非默认路径：
playwright install-deps chromium
```

## 5. xsec_token 失效导致无法访问笔记

**症状**：笔记 URL 打开显示「内容不存在」

**原因**：小红书链接有防盗链 token，有效期通常 24 小时以内

**解决方案**：
- 采集时同步抓取笔记正文
- 优先采集笔记内容而非仅保存链接