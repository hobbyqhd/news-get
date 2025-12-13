"""每日爬取脚本 - 用于 GitHub Actions
自动爬取过去一周的数据，已存在的文件不会覆盖
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.news_crawler_v2 import crawl_and_save_news_items
from src.reports.daily_report import DailyReport
from src.utils.file_manager import get_report_file_path

logger = logging.getLogger(__name__)


def setup_logging():
    """设置日志配置"""
    # 确保日志目录存在
    log_dir = project_root / 'data' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / f'daily_{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )


def main():
    """主函数"""
    setup_logging()
    logger.info("=" * 60)
    logger.info("每日新闻爬取任务开始（过去一周）")
    logger.info("=" * 60)
    
    # 爬取过去一周的数据（包括今天，共7天）
    today = datetime.now()
    dates_to_crawl = []
    for i in range(7):
        date = today - timedelta(days=i)
        dates_to_crawl.append(date)
    
    # 从旧到新排序
    dates_to_crawl.reverse()
    
    logger.info(f"目标日期范围: {dates_to_crawl[0].strftime('%Y-%m-%d')} 到 {dates_to_crawl[-1].strftime('%Y-%m-%d')}")
    logger.info(f"共 {len(dates_to_crawl)} 天")
    
    # 创建报告（使用今天作为报告日期，并记录日期范围）
    date_range = (dates_to_crawl[0], dates_to_crawl[-1])
    report = DailyReport(today, date_range=date_range)
    
    # 统计信息
    total_stats = {"success": 0, "failed": 0, "skipped": 0}
    all_news_items = []
    generated_files = []  # 记录本次生成的 md 文件
    
    # 遍历每一天进行爬取
    for date in dates_to_crawl:
        logger.info("")
        logger.info(f"处理日期: {date.strftime('%Y-%m-%d')}")
        logger.info("-" * 60)
        
        # 执行爬取（skip_existing=True 确保不覆盖已存在的文件）
        result = crawl_and_save_news_items(date)
        
        stats = result["stats"]
        news_items = result["items"]
        
        # 累计统计信息
        total_stats["success"] += stats["success"]
        total_stats["failed"] += stats["failed"]
        total_stats["skipped"] += stats["skipped"]
        
        # 更新报告
        for item in news_items:
            report.add_success(item)
            all_news_items.append(item)
            # 记录生成的 md 文件
            md_filename = f"{date.strftime('%Y%m%d')}.md"
            if md_filename not in generated_files:
                generated_files.append(md_filename)
        
        if stats["failed"] > 0:
            report.add_failed(date)
        
        if stats["skipped"] > 0:
            report.add_skipped(stats["skipped"])
        
        # 输出当日结果
        logger.info(f"  ✓ 成功: {stats['success']} 条")
        logger.info(f"  ✗ 失败: {stats['failed']} 条")
        logger.info(f"  ⏭ 跳过: {stats['skipped']} 条（已存在）")
    
    # 保存生成的 md 文件列表到文件
    if generated_files:
        new_files_path = project_root / 'data' / 'new_files.txt'
        with open(new_files_path, 'w') as f:
            for filename in generated_files:
                f.write(f"data/news/{filename}\n")
        logger.info(f"✓ 新文件列表已保存: {new_files_path}")
    else:
        logger.info("没有新生成的 md 文件")
    
    # 输出总体统计信息
    logger.info("")
    logger.info("=" * 60)
    logger.info("爬取完成（过去一周）")
    logger.info(f"总计成功: {total_stats['success']} 条")
    logger.info(f"总计失败: {total_stats['failed']} 条")
    logger.info(f"总计跳过: {total_stats['skipped']} 条（已存在）")
    logger.info("=" * 60)
    
    # 输出成功爬取的新闻列表和URL
    if all_news_items:
        logger.info("\n成功爬取的新闻:")
        for item in sorted(all_news_items, key=lambda x: x.date):
            logger.info(f"  - {item.date.strftime('%Y-%m-%d')}: {item.title}")
            logger.info(f"    URL: {item.url}")
    else:
        logger.info("\n没有新爬取的新闻（可能都已存在）")
    
    # 如果报告已保存，输出报告路径
    if report_path:
        logger.info(f"\n报告文件: {report_path}")
    
    # 返回退出码（总是成功，只要有尝试）
    return 0


if __name__ == '__main__':
    sys.exit(main())

