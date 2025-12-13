"""爬虫模块"""

from .news_crawler import (
    crawl_and_save_from_directory,
    fetch_news_by_url,
    fetch_news_by_date,
    build_directory_url,
    build_news_url,
    extract_date_from_title,
    fetch_news_links_from_directory,
    crawl_news_from_directory,
    check_news_file_exists,
    save_news_to_file,
    format_news_content,
    record_missing_date,
    update_not_exist_file,
    remove_date_from_not_exist
)

# 确保 remove_date_from_not_exist 存在（向后兼容）
try:
    from .news_crawler import remove_date_from_not_exist
except ImportError:
    # 如果不存在，定义一个空函数
    def remove_date_from_not_exist(date):
        pass

__all__ = [
    'crawl_and_save_from_directory',
    'fetch_news_by_url',
    'fetch_news_by_date',
    'build_directory_url',
    'build_news_url',
    'extract_date_from_title',
    'fetch_news_links_from_directory',
    'crawl_news_from_directory',
    'check_news_file_exists',
    'save_news_to_file',
    'format_news_content',
    'record_missing_date',
    'update_not_exist_file',
    'remove_date_from_not_exist'
]

