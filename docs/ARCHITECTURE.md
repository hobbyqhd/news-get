# 项目架构文档

## 目录结构

```
news-get/
├── .github/
│   └── workflows/
│       └── daily.yml              # GitHub Actions 每日任务
├── src/
│   ├── crawler/                   # 爬虫模块
│   │   ├── news_crawler.py       # 核心爬虫逻辑（原版）
│   │   └── news_crawler_v2.py    # 新版爬虫（返回 NewsItem）
│   ├── models/                    # 数据模型
│   │   └── news_item.py          # 新闻数据模型（包含URL）
│   ├── utils/                     # 工具函数
│   │   └── file_manager.py       # 文件管理
│   └── reports/                   # 报告生成
│       └── daily_report.py        # 每日报告生成
├── scripts/
│   ├── crawl_news.py             # 命令行工具（兼容旧版）
│   └── daily_crawl.py            # 每日爬取脚本（GitHub Actions用）
├── data/
│   ├── news/                     # 新闻数据（YYYYMMDD.md）
│   ├── logs/                     # 日志文件
│   └── reports/                  # 每日报告（YYYY-MM-DD.md）
└── config/
    └── config.example.py         # 配置示例
```

## 核心模块说明

### 1. 数据模型 (`src/models/news_item.py`)

`NewsItem` 数据类，包含：
- `title`: 标题
- `content`: 内容
- `date`: 实际日期
- `url`: **实际页面URL**（重要！）
- `source_url`: 来源URL（目录页面）
- `crawled_at`: 爬取时间

### 2. 爬虫模块 (`src/crawler/`)

- `news_crawler.py`: 原版爬虫，返回元组 `(title, content, date)`
- `news_crawler_v2.py`: 新版爬虫，返回 `NewsItem` 对象，**包含实际URL**

### 3. 报告模块 (`src/reports/daily_report.py`)

`DailyReport` 类：
- 记录成功/失败/跳过的统计
- 生成 Markdown 格式的每日报告
- 报告包含：新闻列表、URL、统计信息

### 4. 每日爬取脚本 (`scripts/daily_crawl.py`)

- 爬取今天的新闻
- 生成每日报告
- 输出新闻列表和URL到日志

## 工作流程

### GitHub Actions 每日执行流程

1. **触发**: 每天北京时间 7:00 (UTC 23:00)
2. **执行**: `scripts/daily_crawl.py`
3. **爬取**: 从目录页面提取实际URL，爬取新闻
4. **保存**: 保存新闻到 `data/news/YYYYMMDD.md`
5. **报告**: 生成报告到 `data/reports/YYYY-MM-DD.md`
6. **提交**: 自动提交新闻文件和报告文件

### 报告格式

每日报告 (`data/reports/YYYY-MM-DD.md`) 包含：

```markdown
# 每日新闻爬取报告 - 2025-12-13

## 📊 统计信息
- ✅ 成功: 3 条
- ❌ 失败: 0 条
- ⏭️  跳过: 2 条（已存在）

## ✅ 成功爬取的新闻
| 日期 | 标题 | URL |
|------|------|-----|
| 2025-12-13 | 每日新闻联播... | http://mrxwlb.com/... |

## 📝 详细信息
（包含每个新闻的详细信息和URL）
```

## URL 处理

**重要**: 所有URL都是实际页面的URL，不是拼接的！

1. 从目录页面 (`http://mrxwlb.com/YYYY/MM/DD/`) 提取新闻链接
2. 每个链接都是实际可访问的新闻页面URL
3. URL保存在 `NewsItem.url` 字段中
4. 报告和日志中都会显示实际URL

## 扩展性

- **模块化设计**: 各模块职责清晰，易于维护
- **数据模型**: 使用 `NewsItem` 统一数据结构
- **报告系统**: 可扩展为周报、月报等
- **日志系统**: 结构化日志，便于追踪

