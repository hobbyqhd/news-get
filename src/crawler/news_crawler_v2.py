"""新版爬虫 - 返回 NewsItem 对象"""

import logging
from datetime import datetime
from typing import List, Optional, Dict
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.news_item import NewsItem
from src.utils.file_manager import check_news_file_exists, save_news_file
from .news_crawler import (
    fetch_news_links_from_directory,
    fetch_news_by_url as _fetch_news_by_url,
    build_directory_url,
    record_missing_date,
    remove_date_from_not_exist
)

logger = logging.getLogger(__name__)


def crawl_news_items_from_directory(
    date: datetime, 
    skip_existing: bool = True
) -> List[NewsItem]:
    """
    从目录页面爬取所有新闻，返回 NewsItem 列表
    
    Args:
        date: 日期对象（目录日期）
        skip_existing: 是否跳过已存在的文件
        
    Returns:
        List[NewsItem]: 新闻列表
    """
    # 获取目录页面的所有新闻链接
    news_links = fetch_news_links_from_directory(date)
    source_url = build_directory_url(date)
    
    if not news_links:
        logger.warning(f"目录页面 {date.strftime('%Y-%m-%d')} 未找到新闻链接")
        return []
    
    # 去重URL
    seen_urls = set()
    unique_links = []
    for link in news_links:
        normalized = link.rstrip('/').split('?')[0]
        if normalized not in seen_urls:
            seen_urls.add(normalized)
            unique_links.append(link)
    
    logger.info(f"去重后剩余 {len(unique_links)} 个唯一新闻链接（原始: {len(news_links)} 个）")
    
    results: List[NewsItem] = []
    seen_results = set()  # 用于去重（标题+日期）
    
    for link in unique_links:
        # 预检查：如果启用跳过已存在文件
        if skip_existing:
            # 尝试从URL路径中提取日期
            import re
            url_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', link)
            if url_match:
                try:
                    year, month, day = int(url_match.group(1)), int(url_match.group(2)), int(url_match.group(3))
                    possible_date = datetime(year, month, day)
                    if check_news_file_exists(possible_date):
                        logger.info(f"⏭ 跳过已存在的新闻（预检查）: {link[:80]}...")
                        continue
                except (ValueError, IndexError):
                    pass
        
        logger.info(f"正在爬取新闻: {link}")
        
        # 使用现有的 fetch_news_by_url 函数爬取单个新闻
        result = _fetch_news_by_url(link, date=None)
        
        if result:
            title, content, actual_date = result
            
            # 再次检查实际日期文件是否存在
            if skip_existing and check_news_file_exists(actual_date):
                logger.info(f"⏭ 跳过已存在的新闻: {actual_date.strftime('%Y-%m-%d')} ({title[:50]}...)")
                continue
            
            # 去重：如果标题和日期相同，跳过
            result_key = (title, actual_date.strftime('%Y-%m-%d'))
            if result_key not in seen_results:
                seen_results.add(result_key)
                
                # 创建 NewsItem 对象
                news_item = NewsItem(
                    title=title,
                    content=content,
                    date=actual_date,
                    url=link,  # 实际页面URL
                    source_url=source_url  # 目录页面URL
                )
                
                results.append(news_item)
                logger.info(f"成功爬取: {title} (实际日期: {actual_date.strftime('%Y-%m-%d')}, URL: {link})")
            else:
                logger.info(f"跳过重复新闻: {title} (实际日期: {actual_date.strftime('%Y-%m-%d')})")
        else:
            logger.warning(f"爬取失败: {link}")
    
    return results


def crawl_and_save_news_items(date: datetime) -> Dict[str, int]:
    """
    从目录页面爬取并保存所有新闻，返回统计信息和 NewsItem 列表
    
    Args:
        date: 日期对象（目录日期）
        
    Returns:
        Dict: 包含统计信息和新闻列表
    """
    stats = {"success": 0, "failed": 0, "skipped": 0}
    news_items: List[NewsItem] = []
    
    # 获取目录页面的所有新闻链接
    news_links = fetch_news_links_from_directory(date)
    
    if not news_links:
        logger.warning(f"目录页面 {date.strftime('%Y-%m-%d')} 未找到新闻链接，记录为缺失")
        record_missing_date(date)
        stats["failed"] = 1
        return {"stats": stats, "items": news_items}
    
    # 爬取所有新闻
    news_items = crawl_news_items_from_directory(date, skip_existing=True)
    
    if not news_items:
        # 检查是否是因为所有文件都已存在
        skipped_count = 0
        import re
        for link in news_links[:10]:  # 只检查前10个链接作为样本
            url_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', link)
            if url_match:
                try:
                    year, month, day = int(url_match.group(1)), int(url_match.group(2)), int(url_match.group(3))
                    check_date = datetime(year, month, day)
                    if check_news_file_exists(check_date):
                        skipped_count += 1
                except (ValueError, IndexError):
                    pass
        
        if skipped_count > 0:
            logger.info(f"目录页面 {date.strftime('%Y-%m-%d')} 的所有新闻文件已存在，无需爬取")
            stats["skipped"] = len(news_links)
        else:
            logger.warning(f"目录页面 {date.strftime('%Y-%m-%d')} 未能成功爬取任何新闻")
            stats["failed"] = 1
        return {"stats": stats, "items": news_items}
    
    # 保存每个新闻
    for item in news_items:
        # 使用 NewsItem 的 to_markdown 方法生成内容
        markdown_content = item.to_markdown()
        file_path = save_news_file(markdown_content, item.date)
        
        if file_path:
            logger.info(f"✓ 成功保存: {file_path} (日期: {item.date.strftime('%Y-%m-%d')}, URL: {item.url})")
            stats["success"] += 1
            # 如果之前该日期被标记为缺失，现在成功爬取，则从not_exist.md中移除
            remove_date_from_not_exist(item.date)
        else:
            logger.warning(f"✗ 保存失败: {item.title} (日期: {item.date.strftime('%Y-%m-%d')})")
            stats["failed"] += 1
            record_missing_date(item.date)
    
    return {"stats": stats, "items": news_items}

