"""新闻爬虫主程序 - 爬取指定日期的新闻"""

import argparse
import logging
from datetime import datetime, timedelta
from src.news_crawler import (
    crawl_and_save, 
    fetch_news_by_date, 
    fetch_news_by_url, 
    save_news_to_file,
    crawl_and_save_from_directory  # 新增：目录页面爬取
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime:
    """
    解析日期字符串
    
    支持格式:
    - YYYY-MM-DD
    - YYYYMMDD
    - today / yesterday / tomorrow
    """
    date_str = date_str.strip().lower()
    
    if date_str == 'today':
        return datetime.now()
    elif date_str == 'yesterday':
        return datetime.now() - timedelta(days=1)
    elif date_str == 'tomorrow':
        return datetime.now() + timedelta(days=1)
    elif len(date_str) == 8 and date_str.isdigit():
        # YYYYMMDD
        return datetime.strptime(date_str, '%Y%m%d')
    else:
        # YYYY-MM-DD
        return datetime.strptime(date_str, '%Y-%m-%d')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='新闻联播爬虫 - 爬取指定日期的新闻并保存为 Markdown 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取今天的新闻
  python crawl_news.py
  
  # 爬取指定日期
  python crawl_news.py --date 2025-11-22
  python crawl_news.py --date 20251122
  
  # 爬取昨天的新闻
  python crawl_news.py --date yesterday
  
  # 批量爬取（最近7天）
  python crawl_news.py --range 7
  
  # 爬取指定日期范围
  python crawl_news.py --start 2025-11-20 --end 2025-11-25
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        type=str,
        default=None,
        help='直接指定新闻URL（用于处理URL不正确的情况）'
    )
    
    parser.add_argument(
        '--date', '-d',
        type=str,
        default='today',
        help='日期 (格式: YYYY-MM-DD, YYYYMMDD, 或 today/yesterday/tomorrow)'
    )
    
    parser.add_argument(
        '--range', '-r',
        type=int,
        help='批量爬取最近N天的新闻'
    )
    
    parser.add_argument(
        '--start', '-s',
        type=str,
        help='开始日期 (用于批量爬取)'
    )
    
    parser.add_argument(
        '--end', '-e',
        type=str,
        help='结束日期 (用于批量爬取)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅测试URL，不实际爬取和保存'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("新闻联播爬虫")
    logger.info("=" * 60)
    
    # 如果指定了URL，直接使用URL爬取
    if args.url:
        logger.info(f"使用指定URL: {args.url}")
        date = parse_date(args.date) if args.date != 'today' else None
        
        result = fetch_news_by_url(args.url, date)
        if result:
            title, content, extracted_date = result
            file_path = save_news_to_file(title, content, extracted_date)
            if file_path:
                logger.info(f"\n✓ 爬取完成！")
                logger.info(f"文件保存位置: {file_path}")
                logger.info(f"使用的日期: {extracted_date.strftime('%Y-%m-%d')}")
            else:
                logger.error("保存文件失败")
        else:
            logger.error("爬取失败")
        return
    
    # 批量爬取模式
    if args.range:
        logger.info(f"批量爬取最近 {args.range} 天的新闻...")
        dates = [datetime.now() - timedelta(days=i) for i in range(args.range)]
        dates.reverse()  # 从旧到新
        
        success_count = 0
        missing_dates = []
        for date in dates:
            logger.info(f"\n处理日期: {date.strftime('%Y-%m-%d')}")
            if args.dry_run:
                from src.news_crawler import build_directory_url
                url = build_directory_url(date)
                logger.info(f"  目录URL: {url}")
            else:
                stats = crawl_and_save_from_directory(date)
                if stats["success"] > 0:
                    success_count += stats["success"]
                    logger.info(f"  ✓ 成功: {stats['success']} 个")
                if stats["skipped"] > 0:
                    logger.info(f"  ⏭ 跳过: {stats['skipped']} 个（已存在）")
                if stats["failed"] > 0:
                    missing_dates.append(date)
                    logger.warning(f"  ✗ 失败: {stats['failed']} 个")
        
        # 更新缺失日期文件
        if missing_dates and not args.dry_run:
            from src.news_crawler import update_not_exist_file
            update_not_exist_file(missing_dates)
        
        logger.info(f"\n完成！成功: {success_count}/{len(dates)}")
        return
    
    # 日期范围模式
    if args.start and args.end:
        logger.info(f"批量爬取日期范围: {args.start} 到 {args.end}")
        start_date = parse_date(args.start)
        end_date = parse_date(args.end)
        
        if start_date > end_date:
            logger.error("开始日期不能晚于结束日期")
            return
        
        current_date = start_date
        success_count = 0
        missing_dates = []
        total_days = (end_date - start_date).days + 1
        
        while current_date <= end_date:
            logger.info(f"\n处理日期: {current_date.strftime('%Y-%m-%d')}")
            if args.dry_run:
                from src.news_crawler import build_directory_url
                url = build_directory_url(current_date)
                logger.info(f"  目录URL: {url}")
            else:
                stats = crawl_and_save_from_directory(current_date)
                if stats["success"] > 0:
                    success_count += stats["success"]
                    logger.info(f"  ✓ 成功: {stats['success']} 个")
                if stats["skipped"] > 0:
                    logger.info(f"  ⏭ 跳过: {stats['skipped']} 个（已存在）")
                if stats["failed"] > 0:
                    missing_dates.append(current_date)
                    logger.warning(f"  ✗ 失败: {stats['failed']} 个")
            
            current_date += timedelta(days=1)
        
        # 更新缺失日期文件
        if missing_dates and not args.dry_run:
            from src.news_crawler import update_not_exist_file
            update_not_exist_file(missing_dates)
        
        logger.info(f"\n完成！成功: {success_count}/{total_days}")
        return
    
    # 单日爬取模式
    try:
        date = parse_date(args.date)
        logger.info(f"目标日期: {date.strftime('%Y-%m-%d')}")
        
        if args.dry_run:
            from src.news_crawler import build_directory_url
            url = build_directory_url(date)
            logger.info(f"目录URL: {url}")
            logger.info("(dry-run 模式，未实际爬取)")
        else:
            stats = crawl_and_save_from_directory(date)
            if stats["success"] > 0 or stats["skipped"] > 0:
                logger.info("\n" + "=" * 60)
                logger.info("✓ 处理完成！")
                if stats["success"] > 0:
                    logger.info(f"成功: {stats['success']} 个")
                if stats["skipped"] > 0:
                    logger.info(f"跳过: {stats['skipped']} 个（已存在）")
                if stats["failed"] > 0:
                    logger.warning(f"失败: {stats['failed']} 个")
                logger.info("=" * 60)
            elif stats["failed"] > 0:
                logger.error("\n✗ 爬取失败")
            elif stats["skipped"] > 0:
                logger.info("\n" + "=" * 60)
                logger.info("✓ 所有新闻文件已存在，无需爬取")
                logger.info(f"跳过: {stats['skipped']} 个（已存在）")
                logger.info("=" * 60)
            else:
                logger.warning("\n⚠ 未找到新闻链接")
                
    except ValueError as e:
        logger.error(f"日期格式错误: {e}")
        logger.error("支持的格式: YYYY-MM-DD, YYYYMMDD, today, yesterday, tomorrow")
    except Exception as e:
        logger.error(f"发生错误: {e}")


if __name__ == '__main__':
    main()

