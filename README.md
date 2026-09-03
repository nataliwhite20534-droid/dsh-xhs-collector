# dsh-xhs-collector

> 在住宅 IP 环境下稳定抓取小红书数据，为 AI 决策提供真实口碑依据。

[![DSH Plugin](https://img.shields.io/badge/DSH-Plugin-blue)](https://github.com/deepseek-ai/deepseek-harness)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## 核心问题

小红书的风控不是技术问题，是经济问题：
平台靠广告收入活着，爬虫直接伤害广告主的投放效果，所以平台会用一切手段阻止数据流出。

dsh-xhs-collector 的设计思路是：**用平台的逻辑对付平台**。

## 工作原理

```
关键词搜索请求
     ↓
CDP 真实 Chrome（住宅 IP 出口）
     ↓
Cookie 自动刷新（每 30 分钟）
     ↓
结构化 JSON 输出（去重 + 字段标准化）
     ↓
→ DSH Agent / 人工分析师 / BI 工具
```

## 功能清单

| 功能 | 说明 |
|------|------|
| 批量关键词搜索 | 一次传入 N 个关键词，并发执行 |
| Cookie 自动收割 | guided_login 扫码一次，后续自动续期 |
| 单笔记去重 | 同一关键词内 noteId 去重 |
| 跨关键词去重 | 全量结果全局去重 |
| 结构化输出 | title / author / likes / noteId / xsec_token / date |
| 增量采集 | 仅拉取新增内容，不重复拉取 |
| 失败重试 | 超时 / 限流自动重试（最多 3 次） |

## 安装

```bash
pip install cn-scraper-mcp>=0.5.0 playwright
playwright install chromium
```

## 快速开始

```python
from cn_scraper import XHSCollector

collector = XHSCollector(
    cookie_path="~/.cn-scraper-cookies/xiaohongshu.json",
    output_dir="./output",
)

collector.guided_login()

results = collector.search_batch(
    keywords=["完美日记", "完美日记推荐", "完美日记测评", "完美日记眼影"],
    max_notes_per_keyword=100,
    deduplicate=True,
)

import json
print(json.dumps(results["summary"], ensure_ascii=False, indent=2))
```

## 输出示例

```json
{
  "keywords_processed": 4,
  "total_raw_notes": 387,
  "total_deduped": 341,
  "dedup_rate": "11.9%",
  "output_file": "./output/xhs_20260903_143022.json",
  "fields": ["noteId", "title", "author", "likes", "date", "note_url"],
  "top_keywords_by_volume": [
    {"keyword": "完美日记", "count": 142},
    {"keyword": "完美日记眼影", "count": 89},
    {"keyword": "完美日记测评", "count": 81},
    {"keyword": "完美日记推荐", "count": 75}
  ]
}
```

## 输出字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| noteId | string | 笔记唯一 ID（用于去重） |
| title | string | 笔记标题 |
| author | string | 作者昵称 |
| likes | int | 点赞数 |
| date | string | 发布日期 YYYY-MM-DD |
| note_url | string | 笔记链接（xsec_token 有时效） |
| keyword | string | 触发该笔记的关键词 |

## 项目结构

```
dsh-xhs-collector/
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── workflows/
│   ├── search.py          # 搜索核心逻辑
│   └── login.py            # Cookie 管理
├── output/                  # 采集结果输出目录（.gitignore）
└── docs/
    ├── cookie-guide.md      # Cookie 获取教程
    ├── case-study.md        # 真实案例：完美日记口碑采集
    └── troubleshooting.md   # 常见问题
```

## 依赖

- [cn-scraper-mcp](https://github.com/) — CDP Chrome 驱动
- [playwright](https://playwright.dev/) — 浏览器自动化
- DSH (可选) — AI Agent 编排层

## 已知限制

| 限制 | 说明 | 应对方案 |
|------|------|----------|
| IP 风控 | 公共 IP 会被限流或弹出验证码 | 使用住宅 IP 或代理池 |
| xsec_token 时效 | 笔记链接中的 token 通常 24h 内失效 | 采集时同步抓取正文内容 |
| 评论区 | 当前版本未覆盖 | Roadmap 中 |
| 搜索结果上限 | 非登录用户约 1000 条/关键词 | 增量 + 多关键词覆盖 |

## Roadmap

- [ ] 评论区和热评抓取
- [ ] 多账号 Cookie 轮换
- [ ] 代理池支持
- [ ] 增量采集（只拉新增）
- [ ] 结果导出为 CSV / Excel

## 真实案例

📊 [完美日记 30 天口碑数据采集完整流程](./docs/case-study.md)

## 🌏 DSH 生态成员

本项目是 **DSH (DeepSeek Harness)** 生态的一员，同系列还有：

- 🎀 [`dsh-moe-plugin`](https://github.com/nataliwhite20534-droid/dsh-moe-plugin) — 萌属性 Persona 系统（10 种预设卡片）
- ⚙️ [`dsh-4-role-workflow`](https://github.com/nataliwhite20534-droid/dsh-4-role-workflow) — 4 角色 Agent 工作流
- 📓 [`dsh-china-research-notes`](https://github.com/nataliwhite20534-droid/dsh-china-research-notes) — 中国平台反爬实战笔记

## 🔗 相关链接

- [DSH (DeepSeek Harness) 主仓](https://github.com/deepseek-ai/deepseek-harness)

## 免责声明

本工具仅供学习和研究使用。请遵守小红书《用户协议》和相关法律法规，
不要大规模爬取或用于商业牟利。数据采集者自行承担使用风险。