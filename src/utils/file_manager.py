"""文件管理工具"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def get_news_file_path(date: datetime, base_dir: Optional[Path] = None) -> Path:
    """
    获取新闻文件路径
    
    Args:
        date: 日期对象
        base_dir: 基础目录，默认为 data/news
        
    Returns:
        Path: 文件路径
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent / 'data' / 'news'
    
    base_dir.mkdir(parents=True, exist_ok=True)
    date_str = date.strftime('%Y%m%d')
    return base_dir / f'{date_str}.md'


def check_news_file_exists(date: datetime, base_dir: Optional[Path] = None) -> bool:
    """
    检查新闻文件是否存在
    
    Args:
        date: 日期对象
        base_dir: 基础目录
        
    Returns:
        bool: 文件是否存在
    """
    file_path = get_news_file_path(date, base_dir)
    return file_path.exists()


def save_news_file(content: str, date: datetime, base_dir: Optional[Path] = None) -> Optional[Path]:
    """
    保存新闻文件
    
    Args:
        content: 文件内容
        date: 日期对象
        base_dir: 基础目录
        
    Returns:
        Path: 保存的文件路径，失败返回None
    """
    try:
        file_path = get_news_file_path(date, base_dir)
        file_path.write_text(content, encoding='utf-8')
        logger.info(f"成功保存文件: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        return None


def get_report_file_path(date: datetime, base_dir: Optional[Path] = None) -> Path:
    """
    获取报告文件路径
    
    Args:
        date: 日期对象
        base_dir: 基础目录，默认为 data/reports
        
    Returns:
        Path: 文件路径
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent / 'data' / 'reports'
    
    base_dir.mkdir(parents=True, exist_ok=True)
    date_str = date.strftime('%Y-%m-%d')
    return base_dir / f'{date_str}.md'

