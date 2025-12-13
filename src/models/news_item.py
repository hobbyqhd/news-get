"""新闻数据模型"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NewsItem:
    """新闻数据模型"""
    title: str              # 标题
    content: str            # 内容
    date: datetime         # 实际日期
    url: str               # 实际页面URL
    source_url: Optional[str] = None  # 来源URL（目录页面）
    crawled_at: Optional[datetime] = None  # 爬取时间
    
    def __post_init__(self):
        """初始化后处理"""
        if self.crawled_at is None:
            from datetime import datetime
            self.crawled_at = datetime.now()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'title': self.title,
            'content': self.content,
            'date': self.date.strftime('%Y-%m-%d'),
            'url': self.url,
            'source_url': self.source_url,
            'crawled_at': self.crawled_at.isoformat() if self.crawled_at else None
        }
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        date_str = self.date.strftime('%Y年%m月%d日')
        return f"""# {self.title}

**日期**: {date_str} ({self.date.strftime('%Y-%m-%d')})
**来源**: [{self.url}]({self.url})
**爬取时间**: {self.crawled_at.strftime('%Y-%m-%d %H:%M:%S') if self.crawled_at else 'N/A'}

---

{self.content}

---

*来源链接: {self.url}*
"""

