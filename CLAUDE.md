# news-get

从 mrxwlb.com 爬取新闻联播文字版，保存为 Markdown，并通过 GitHub Actions 定时爬取。

## 常用命令

```bash
pip install -r requirements.txt          # 安装依赖
python scripts/daily_crawl.py            # 每日爬取（过去 7 天，CI 入口）
python scripts/merge_all_monthly_news.py # 合并月度汇总
```

## 技术栈

- Python 3.10+
- requests, beautifulsoup4, lxml（HTTP 爬取）
- selenium, webdriver-manager（部分页面需浏览器）
- GitHub Actions + Chrome/ChromeDriver（CI 环境）

## 项目结构

| 路径 | 说明 |
|------|------|
| `scripts/daily_crawl.py` | CI 主入口，爬取过去一周新闻 |
| `src/crawler/news_crawler.py` | 爬虫核心（URL 构建、页面解析） |
| `src/crawler/news_crawler_v2.py` | 新版爬虫，返回 `NewsItem` 对象 |
| `src/models/news_item.py` | 新闻数据模型 |
| `src/utils/file_manager.py` | 文件路径与读写 |
| `src/reports/daily_report.py` | 日报生成 |
| `data/news/YYYYMMDD.md` | 新闻存储（按实际日期命名） |
| `data/news/not_exist.md` | 缺失日期记录 |
| `data/reports/` | 月度汇总 |
| `.github/workflows/daily-crawl.yml` | 每小时自动爬取 |

## 架构要点

- **v2 是活跃版本**：`news_crawler_v2.py` 调用 `news_crawler.py` 的底层函数，对外返回 `NewsItem` 列表
- **日期逻辑**：目录页日期可能与新闻实际日期不同，以页面标题解析出的实际日期为准保存文件
- **去重策略**：`skip_existing=True` 时跳过已存在的 `data/news/YYYYMMDD.md`
- **时区**：CI 使用 `Asia/Shanghai`

## 开发约定

- 使用 `logging` 模块，不用 `print` 做正式日志
- 文件读写统一 UTF-8 编码
- 新增爬虫逻辑优先扩展 `news_crawler_v2.py`，底层解析放 `news_crawler.py`
- 不要覆盖 `data/news/` 中已有文件，除非用户明确要求
- 不要提交 `.env`、`config.py`（含密钥）

## 注意事项

- `data/news/` 和 `data/reports/` 含大量历史数据，修改爬虫时避免批量重写
- CI 需要 Chrome + ChromeDriver，本地调试 Selenium 相关功能时需安装 Chrome
