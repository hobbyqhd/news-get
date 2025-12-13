# 项目重构计划

## 目标
1. 模块化、分层的项目结构
2. GitHub Actions 每天自动执行并生成报告
3. 报告包含抓取的新闻列表和实际URL
4. 使用实际页面URL（已实现）

## 新目录结构

```
news-get/
├── .github/
│   └── workflows/
│       └── daily.yml              # GitHub Actions 每日任务
├── src/
│   ├── __init__.py
│   ├── crawler/                   # 爬虫模块
│   │   ├── __init__.py
│   │   ├── news_crawler.py       # 核心爬虫逻辑
│   │   └── url_extractor.py      # URL提取逻辑
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   └── news_item.py          # 新闻数据模型（包含URL）
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── file_manager.py        # 文件管理
│   │   └── logger.py             # 日志配置
│   └── reports/                   # 报告生成
│       ├── __init__.py
│       └── daily_report.py       # 每日报告生成
├── scripts/
│   ├── crawl_news.py             # 命令行工具
│   └── daily_crawl.py            # 每日爬取脚本（GitHub Actions用）
├── data/
│   ├── news/                     # 新闻数据（YYYYMMDD.md）
│   ├── logs/                     # 日志文件
│   └── reports/                  # 每日报告（YYYY-MM-DD.md）
├── config/
│   └── config.example.py         # 配置示例
├── tests/                         # 测试文件
├── docs/                          # 文档
│   ├── API.md                    # API文档
│   └── ARCHITECTURE.md           # 架构文档
├── requirements.txt
├── README.md
└── .gitignore
```

## 数据模型设计

```python
@dataclass
class NewsItem:
    title: str           # 标题
    content: str         # 内容
    date: datetime      # 实际日期
    url: str            # 实际页面URL
    source_url: str     # 来源URL（目录页面）
    crawled_at: datetime # 爬取时间
```

## 报告格式

每日报告（data/reports/YYYY-MM-DD.md）：
- 爬取日期
- 成功/失败/跳过统计
- 新闻列表（标题、日期、URL）
- 缺失日期列表

