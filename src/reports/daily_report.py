"""每日报告生成模块"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from src.models.news_item import NewsItem
from src.utils.file_manager import get_report_file_path

logger = logging.getLogger(__name__)


class DailyReport:
    """每日爬取报告"""
    
    def __init__(self, crawl_date: datetime, date_range: Optional[tuple] = None):
        """
        初始化报告
        
        Args:
            crawl_date: 报告日期（通常是今天）
            date_range: 可选，日期范围 (start_date, end_date)
        """
        self.crawl_date = crawl_date
        self.date_range = date_range
        self.success_items: List[NewsItem] = []
        self.failed_dates: List[datetime] = []
        self.skipped_count: int = 0
        self.stats: Dict[str, int] = {
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def add_success(self, item: NewsItem):
        """添加成功爬取的新闻"""
        self.success_items.append(item)
        self.stats['success'] += 1
    
    def add_failed(self, date: datetime):
        """添加失败的日期"""
        self.failed_dates.append(date)
        self.stats['failed'] += 1
    
    def add_skipped(self, count: int = 1):
        """添加跳过的数量"""
        self.skipped_count += count
        self.stats['skipped'] += count
    
    def generate_markdown(self) -> str:
        """生成Markdown格式的报告"""
        report_date = self.crawl_date.strftime('%Y-%m-%d')
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建标题
        if self.date_range:
            start_date, end_date = self.date_range
            title = f"# 每日新闻爬取报告 - {report_date}（{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}）"
        else:
            title = f"# 每日新闻爬取报告 - {report_date}"
        
        lines = [
            title,
            "",
            f"**生成时间**: {report_time}",
        ]
        
        # 如果有日期范围，显示范围信息
        if self.date_range:
            start_date, end_date = self.date_range
            lines.extend([
                f"**爬取日期范围**: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
                "",
            ])
        
        lines.extend([
            "## 📊 统计信息",
            "",
            f"- ✅ **成功**: {self.stats['success']} 条",
            f"- ❌ **失败**: {self.stats['failed']} 条",
            f"- ⏭️  **跳过**: {self.stats['skipped']} 条（已存在）",
            "",
        ])
        
        # 成功爬取的新闻列表
        if self.success_items:
            lines.extend([
                "## ✅ 成功爬取的新闻",
                "",
                "| 日期 | 标题 | URL |",
                "|------|------|-----|"
            ])
            
            for item in sorted(self.success_items, key=lambda x: x.date):
                date_str = item.date.strftime('%Y-%m-%d')
                title_short = item.title[:50] + "..." if len(item.title) > 50 else item.title
                lines.append(f"| {date_str} | {title_short} | [{item.url}]({item.url}) |")
            
            lines.append("")
        
        # 失败的日期列表
        if self.failed_dates:
            lines.extend([
                "## ❌ 失败的日期",
                "",
            ])
            
            for date in sorted(set(self.failed_dates)):
                date_str = date.strftime('%Y-%m-%d')
                lines.append(f"- {date_str}")
            
            lines.append("")
        
        # 详细信息
        if self.success_items:
            lines.extend([
                "## 📝 详细信息",
                "",
            ])
            
            for item in sorted(self.success_items, key=lambda x: x.date):
                date_str = item.date.strftime('%Y-%m-%d')
                lines.extend([
                    f"### {date_str} - {item.title}",
                    "",
                    f"- **URL**: [{item.url}]({item.url})",
                    f"- **爬取时间**: {item.crawled_at.strftime('%Y-%m-%d %H:%M:%S') if item.crawled_at else 'N/A'}",
                    ""
                ])
        
        return "\n".join(lines)
    
    def save(self, base_dir: Optional[Path] = None) -> Optional[Path]:
        """
        保存报告到文件
        
        Args:
            base_dir: 基础目录
            
        Returns:
            Path: 保存的文件路径，失败返回None
        """
        try:
            report_path = get_report_file_path(self.crawl_date, base_dir)
            content = self.generate_markdown()
            report_path.write_text(content, encoding='utf-8')
            logger.info(f"报告已保存: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return None

