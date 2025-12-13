# 新闻联播爬虫

一个专门用于爬取新闻联播文字版的爬虫工具。

## 📋 项目简介

本项目从 `mrxwlb.com` 网站爬取新闻联播文字版内容，自动格式化并保存为 Markdown 文件。

## ✨ 功能特性

- 🕷️ **自动爬取**: 从 `mrxwlb.com` 爬取指定日期的新闻
- 📝 **Markdown 格式**: 自动格式化内容为 Markdown
- 📅 **批量处理**: 支持单日、日期范围、最近N天等多种爬取模式
- 🔄 **智能去重**: 自动跳过已存在的新闻文件
- 📊 **进度追踪**: 记录缺失日期到 `not_exist.md`

## 🛠️ 技术栈

- **Python 3.10+**
- **爬虫**: `requests`, `beautifulsoup4`, `lxml`
- **环境管理**: `python-dotenv`

## 📁 项目结构

```
news-get/
├── crawl_news.py              # 主程序入口
├── src/
│   └── news_crawler.py        # 爬虫核心模块
├── check_progress.sh          # 进度检查脚本
├── data/
│   └── news/                  # 新闻数据目录（YYYYMMDD.md格式）
│       └── not_exist.md       # 缺失日期记录
├── requirements.txt           # 依赖列表
├── NEWS_CRAWLER_README.md     # 详细使用说明
├── CRAWLER_DESIGN.md          # 爬虫设计文档
└── README.md                  # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

```bash
# 爬取今天的新闻
python crawl_news.py

# 爬取指定日期
python crawl_news.py --date 2025-11-22

# 爬取最近7天
python crawl_news.py --range 7

# 爬取日期范围
python crawl_news.py --start 2025-11-20 --end 2025-11-25

# 使用URL直接爬取
python crawl_news.py --url "http://mrxwlb.com/2025/11/22/..."
```

## 📖 详细使用说明

更多使用说明请参考 [NEWS_CRAWLER_README.md](NEWS_CRAWLER_README.md)

## 🔧 爬虫逻辑

### 目录页面爬取

1. 访问目录页面：`http://mrxwlb.com/YYYY/MM/DD/`
2. 提取所有新闻链接
3. 访问每个新闻页面，提取实际日期（从标题中）
4. 根据实际日期保存文件：`data/news/YYYYMMDD.md`

### 文件保存

- **目录**: `data/news/`
- **文件名格式**: `YYYYMMDD.md`
- **内容格式**: Markdown，包含标题、日期、格式化后的新闻内容

### 缺失日期记录

如果某个日期的目录页面不存在或无法提取新闻链接，会记录到 `data/news/not_exist.md` 文件中。

## 📝 命令行参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--date` | `-d` | 指定日期 | `--date 2025-11-22` |
| `--range` | `-r` | 批量爬取最近N天 | `--range 7` |
| `--start` | `-s` | 开始日期（批量） | `--start 2025-11-20` |
| `--end` | `-e` | 结束日期（批量） | `--end 2025-11-25` |
| `--url` | `-u` | 直接指定URL | `--url "http://..."` |
| `--dry-run` | - | 测试模式（不实际爬取） | `--dry-run` |

## 📊 进度监控

使用 `check_progress.sh` 脚本监控爬取进度：

```bash
./check_progress.sh
```

## ⚠️ 注意事项

1. **网络连接**: 需要能够访问 `mrxwlb.com` 网站
2. **请求频率**: 建议适当控制爬取速度，避免对服务器造成压力
3. **文件覆盖**: 如果同一日期有多个新闻，最新的会覆盖之前的
4. **缺失日期**: 某些日期可能确实没有新闻，会被记录到 `not_exist.md`

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
