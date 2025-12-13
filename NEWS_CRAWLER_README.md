# 新闻爬虫使用说明

## 功能简介

这是一个专门用于爬取新闻联播文字版的爬虫工具，支持：
- ✅ 按日期爬取指定日期的新闻
- ✅ 自动格式化内容为 Markdown
- ✅ 保存到 `data/news/YYYYMMDD.md` 文件
- ✅ 支持批量爬取

## 快速开始

### 1. 爬取今天的新闻

```bash
python crawl_news.py
```

### 2. 爬取指定日期

```bash
# 使用 YYYY-MM-DD 格式
python crawl_news.py --date 2025-11-22

# 使用 YYYYMMDD 格式
python crawl_news.py --date 20251122

# 使用关键字
python crawl_news.py --date yesterday
python crawl_news.py --date today
python crawl_news.py --date tomorrow
```

### 3. 批量爬取

```bash
# 爬取最近7天的新闻
python crawl_news.py --range 7

# 爬取指定日期范围
python crawl_news.py --start 2025-11-20 --end 2025-11-25
```

### 4. 测试模式（不实际爬取）

```bash
python crawl_news.py --date 2025-11-22 --dry-run
```

## URL 格式

爬虫会自动构建URL，格式为：
```
http://mrxwlb.com/YYYY/MM/DD/YYYY年MM月DD日新闻联播文字版/
```

例如：
- `http://mrxwlb.com/2025/11/22/2025年11月22日新闻联播文字版/`

## 文件保存

- **目录**: `data/news/`
- **文件名格式**: `YYYYMMDD.md`
- **文件内容**: 包含标题、日期、格式化后的新闻内容和来源链接

## 内容格式化

爬虫会自动格式化内容：
- 识别标题（【】格式）
- 识别章节（数字编号）
- 整理段落
- 去除广告和导航链接

## 命令行参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--date` | `-d` | 指定日期 | `--date 2025-11-22` |
| `--range` | `-r` | 批量爬取最近N天 | `--range 7` |
| `--start` | `-s` | 开始日期（批量） | `--start 2025-11-20` |
| `--end` | `-e` | 结束日期（批量） | `--end 2025-11-25` |
| `--dry-run` | - | 测试模式 | `--dry-run` |

## 使用示例

### 示例1: 爬取单日新闻

```bash
python crawl_news.py --date 2025-11-22
```

输出：
```
============================================================
新闻联播爬虫
============================================================
目标日期: 2025-11-22
正在爬取: http://mrxwlb.com/2025/11/22/...
成功爬取文章，内容长度: 7542 字符
新闻已保存到: data/news/20251122.md
✓ 爬取完成！
```

### 示例2: 批量爬取最近一周

```bash
python crawl_news.py --range 7
```

### 示例3: 爬取指定日期范围

```bash
python crawl_news.py --start 2025-11-20 --end 2025-11-25
```

## 代码使用

### 在 Python 代码中使用

```python
from datetime import datetime
from src.news_crawler import crawl_and_save, fetch_news_by_date

# 方法1: 直接爬取并保存
date = datetime(2025, 11, 22)
file_path = crawl_and_save(date)
print(f"保存到: {file_path}")

# 方法2: 只爬取不保存
title, content = fetch_news_by_date(date)
print(f"标题: {title}")
print(f"内容长度: {len(content)} 字符")
```

## 注意事项

1. **网络连接**: 确保能够访问 `http://mrxwlb.com`
2. **日期格式**: 支持多种日期格式，推荐使用 `YYYY-MM-DD`
3. **文件覆盖**: 如果文件已存在，会被覆盖
4. **错误处理**: 如果某日期的新闻不存在，会记录错误但继续执行（批量模式）

## 文件结构

```
data/news/
├── 20251122.md
├── 20251123.md
└── ...
```

每个文件包含：
- 标题
- 日期信息
- 爬取时间
- 格式化后的新闻内容
- 来源链接

## 故障排除

### 问题1: 网络连接失败

```
网络请求失败: ...
```

**解决方案**: 检查网络连接，确保可以访问目标网站

### 问题2: 找不到文章内容

```
未找到文章正文内容
```

**解决方案**: 
- 确认该日期是否有新闻
- 检查网站结构是否变化

### 问题3: 日期格式错误

```
日期格式错误: ...
```

**解决方案**: 使用支持的格式：`YYYY-MM-DD`, `YYYYMMDD`, `today`, `yesterday`, `tomorrow`

