"""新闻爬虫模块 - 从 mrxwlb.com 爬取指定日期的新闻"""

import requests
from bs4 import BeautifulSoup
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict
import re
from urllib.parse import quote, urljoin, urlparse

logger = logging.getLogger(__name__)


def build_directory_url(date: datetime, use_zero_padding: bool = True) -> str:
    """
    构建目录页面URL
    
    Args:
        date: 日期对象
        use_zero_padding: 是否使用前导零（True: 01/07, False: 1/7）
        
    Returns:
        str: 目录页面URL
    """
    year = date.year
    month = date.month
    day = date.day

    if use_zero_padding:
        url = f"http://mrxwlb.com/{year}/{month:02d}/{day:02d}/"
    else:
        url = f"http://mrxwlb.com/{year}/{month}/{day}/"

    return url


def build_govopendata_url(date: datetime) -> str:
    """
    构建 govopendata 的新闻URL，格式示例: https://cn.govopendata.com/xinwenlianbo/20250121/
    """
    return f"https://cn.govopendata.com/xinwenlianbo/{date.strftime('%Y%m%d')}/"


def build_news_url(date: datetime, use_zero_padding: bool = True) -> str:
    """
    构建新闻URL

    Args:
        date: 日期对象
        use_zero_padding: 是否使用前导零（True: 01/07, False: 1/7）

    Returns:
        str: 新闻URL
    """
    year = date.year
    month = date.month
    day = date.day

    # URL格式: http://mrxwlb.com/YYYY/MM/DD/2025年MM月DD日新闻联播文字版/
    date_str_cn = f"{year}年{month:02d}月{day:02d}日"
    date_str_cn_encoded = quote(date_str_cn.encode('utf-8'))

    if use_zero_padding:
        # 两位数格式：01/07
        url = f"http://mrxwlb.com/{year}/{month:02d}/{day:02d}/{date_str_cn_encoded}新闻联播文字版/"
    else:
        # 个位数格式：1/7（但中文日期仍使用两位数）
        url = f"http://mrxwlb.com/{year}/{month}/{day}/{date_str_cn_encoded}新闻联播文字版/"

    return url


def format_news_content(content: str) -> str:
    """
    格式化新闻内容，保持与网页一致的格式
    
    Args:
        content: 原始内容
        
    Returns:
        str: 格式化后的内容
    """
    # 按行分割，保留空行结构
    lines = content.split('\n')
    
    formatted_lines = []
    in_main_content = False  # 是否在"主要内容"部分
    in_detail_content = False  # 是否在"详细文字版全文"部分
    current_paragraph = []  # 当前段落
    next_line_is_title = False  # 标记下一行应该是标题（在"以下为详细的文字版全文："之后）
    prev_line = ""  # 上一行内容，用于去重
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 跳过完全空白的行（但保留段落间的空行）
        if not line:
            if current_paragraph:
                # 段落结束，添加段落
                formatted_lines.append(' '.join(current_paragraph))
                formatted_lines.append('')
                current_paragraph = []
            continue
        
        # 检测"今日新闻联播主要内容："标题
        if '今日新闻联播主要内容' in line or '新闻联播主要内容' in line:
            # 确保前面没有未完成的段落
            if current_paragraph:
                formatted_lines.append(' '.join(current_paragraph))
                formatted_lines.append('')
                current_paragraph = []
            formatted_lines.append(line)
            formatted_lines.append('')
            in_main_content = True
            prev_line = line
            continue
        
        # 检测"以下为详细的文字版全文："分隔符
        if '以下为详细的文字版全文' in line or '以下为详细' in line:
            # 确保前面没有未完成的段落
            if current_paragraph:
                formatted_lines.append(' '.join(current_paragraph))
                formatted_lines.append('')
                current_paragraph = []
            # 如果前面有主要内容列表，确保分隔符单独成行
            if in_main_content:
                formatted_lines.append('')
            formatted_lines.append(line)
            formatted_lines.append('')
            in_main_content = False
            in_detail_content = True
            # 标记：下一行应该是标题
            next_line_is_title = True
            prev_line = line
            continue
        
        # 主要内容部分：每行作为一个列表项
        if in_main_content and not in_detail_content:
            # 检测是否是标题行（包含【】）
            if re.match(r'^【.*】', line):
                formatted_lines.append(f"* {line}")
            else:
                formatted_lines.append(f"* {line}")
            continue
        
        # 详细内容部分：保持段落结构
        if in_detail_content:
            # 如果标记了下一行应该是标题，且当前行符合标题特征
            if next_line_is_title:
                if (len(line) >= 8 and len(line) <= 60 and 
                    not re.search(r'[。！？；]$', line) and
                    not re.search(r'^[一二三四五六七八九十]+[、.]', line) and
                    not re.search(r'^\d+[、.]', line)):
                    # 先保存当前段落
                    if current_paragraph:
                        formatted_lines.append(' '.join(current_paragraph))
                        formatted_lines.append('')
                        current_paragraph = []
                    # 添加标题
                    formatted_lines.append(f"### {line}")
                    formatted_lines.append('')
                    next_line_is_title = False
                    prev_line = line  # 记录标题
                    continue
            
            # 跳过与上一行完全相同的重复行（常见于网页格式）
            if line == prev_line and line.strip():
                prev_line = line
                continue
            
            # 检测标题行（包含【】）
            if re.match(r'^【.*】', line):
                # 先保存当前段落
                if current_paragraph:
                    formatted_lines.append(' '.join(current_paragraph))
                    formatted_lines.append('')
                    current_paragraph = []
                # 添加标题
                formatted_lines.append(f"## {line}")
                formatted_lines.append('')
                prev_line = line
            # 检测小标题（数字编号或括号）
            elif re.match(r'^\d+[、.]', line) or re.match(r'^[（(].*[）)]', line):
                if current_paragraph:
                    formatted_lines.append(' '.join(current_paragraph))
                    formatted_lines.append('')
                    current_paragraph = []
                formatted_lines.append(f"### {line}")
                formatted_lines.append('')
                prev_line = line
            # 检测新闻标题
            # 特征：1. 长度适中（8-60字符）
            #       2. 不包含句号、问号、感叹号等结尾标点
            #       3. 不包含日期格式（如"11月12日"）
            #       4. 不包含"当地时间"、"今天"等时间词
            #       5. 下一行是段落内容（包含日期、机构名或较长文本）
            elif (len(line) >= 8 and len(line) <= 60 and 
                  not re.search(r'[。！？；]$', line) and
                  not re.search(r'^[一二三四五六七八九十]+[、.]', line) and
                  not re.search(r'^\d+[、.]', line) and
                  not re.search(r'\d+月\d+日', line) and
                  not re.search(r'当地时间|今天\(|昨日\(', line)):
                
                # 检查下一行是否是段落内容
                next_line_idx = i + 1
                is_title = False
                
                # 跳过空行，查找下一行非空内容
                while next_line_idx < len(lines):
                    next_line = lines[next_line_idx].strip()
                    if not next_line:
                        next_line_idx += 1
                        continue
                    
                    # 如果下一行包含日期、机构名，或长度较长，则当前行是标题
                    if (re.search(r'\d+月\d+日|当地时间|今天\(|国家|国务院|中共中央|全国|教育部|工业和信息化部|市场监管总局', next_line) or
                        len(next_line) > 50):
                        is_title = True
                    break
                
                if is_title:
                    # 先保存当前段落
                    if current_paragraph:
                        formatted_lines.append(' '.join(current_paragraph))
                        formatted_lines.append('')
                        current_paragraph = []
                    # 添加标题（使用三级标题）
                    formatted_lines.append(f"### {line}")
                    formatted_lines.append('')
                    prev_line = line
                else:
                    # 普通段落内容
                    if current_paragraph:
                        formatted_lines.append(' '.join(current_paragraph))
                        formatted_lines.append('')
                        current_paragraph = []
                    if line:
                        formatted_lines.append(line)
                        formatted_lines.append('')
                        prev_line = line
            # 普通段落内容 - 每行作为一个独立段落
            else:
                # 如果当前段落不为空，先保存
                if current_paragraph:
                    formatted_lines.append(' '.join(current_paragraph))
                    formatted_lines.append('')
                    current_paragraph = []
                # 当前行作为新段落
                if line:
                    formatted_lines.append(line)
                    formatted_lines.append('')
                    prev_line = line
        else:
            # 如果不在任何特定部分，按普通段落处理
            if current_paragraph:
                formatted_lines.append(' '.join(current_paragraph))
                formatted_lines.append('')
                current_paragraph = []
            if line:
                formatted_lines.append(line)
                formatted_lines.append('')
    
    # 处理最后一段
    if current_paragraph:
        formatted_lines.append(' '.join(current_paragraph))
    
    # 清理多余的空行（最多保留一个空行）
    result_lines = []
    prev_empty = False
    for line in formatted_lines:
        if not line.strip():
            if not prev_empty:
                result_lines.append('')
                prev_empty = True
        else:
            result_lines.append(line)
            prev_empty = False
    
    return '\n'.join(result_lines)


def extract_date_from_title(title: str) -> Optional[datetime]:
    """
    从新闻标题中提取日期
    例如: "2025年11月02日新闻联播文字版" -> datetime(2025, 11, 2)
    """
    import re
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', title)
    if match:
        try:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return datetime(year, month, day)
        except ValueError:
            return None
    return None


def extract_news_links_from_html(html: str, base_url: str) -> List[str]:
    """
    从目录页面HTML中提取所有新闻链接
    
    Args:
        html: 目录页面的HTML内容
        base_url: 基础URL（用于处理相对链接）
        
    Returns:
        List[str]: 新闻链接列表
    """
    from urllib.parse import unquote
    
    soup = BeautifulSoup(html, 'lxml')
    news_links = []
    
    # 查找所有链接
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '').strip()
        if not href or href.startswith('#'):
            continue
        
        # 处理相对链接
        if not href.startswith('http'):
            href = urljoin(base_url, href)
        
        # URL路径应该包含日期格式 YYYY/MM/DD/
        url_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', href)
        if not url_match:
            continue
        
        # 解码URL以检查内容
        decoded_href = unquote(href)
        
        # 检查是否是新闻链接：
        # 1. URL路径符合日期格式 YYYY/MM/DD/...
        # 2. 解码后的URL或链接文本包含"新闻联播"或"文字版"
        # 3. 链接文本包含日期格式
        link_text = link.get_text(strip=True)
        
        is_news_link = (
            # URL解码后包含日期和新闻联播关键词
            (re.search(r'\d{4}年\d{1,2}月\d{1,2}日', decoded_href) and 
             re.search(r'新闻联播|文字版', decoded_href)) or
            # 链接文本包含日期和新闻联播
            (re.search(r'\d{4}年\d{1,2}月\d{1,2}日', link_text) and 
             re.search(r'新闻联播|文字版', link_text)) or
            # URL路径深度符合新闻文章格式（YYYY/MM/DD/文章名/）
            (href.count('/') >= 5 and href.endswith('/') and 
             'mrxwlb.com' in href and len(href) > len(base_url) + 10)
        )
        
        if is_news_link:
            news_links.append(href)
    
    # 去重
    return list(set(news_links))


def fetch_news_links_from_directory(date: datetime) -> List[str]:
    """
    从目录页面提取所有新闻链接
    
    Args:
        date: 日期对象（目录日期）
        
    Returns:
        List[str]: 新闻链接列表，如果目录页面404或为空则返回空列表
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 尝试两种URL格式
    url_formats = [
        (True, "两位数格式"),
        (False, "个位数格式"),
    ]
    
    for use_zero_padding, format_name in url_formats:
        directory_url = build_directory_url(date, use_zero_padding=use_zero_padding)
        logger.info(f"正在访问目录页面 ({format_name}): {directory_url}")
        
        try:
            response = requests.get(directory_url, headers=headers, timeout=15)
            
            if response.status_code == 404:
                logger.warning(f"目录页面不存在 ({format_name}): {directory_url}")
                if not use_zero_padding:
                    # 两种格式都404，返回空列表
                    return []
                continue  # 尝试下一个格式
            
            if response.status_code == 403:
                logger.warning(f"目录页面访问被拒绝 ({format_name}): {directory_url} (403 Forbidden)")
                # 403可能是反爬虫，等待后重试或跳过
                import time
                time.sleep(3)  # 等待3秒
                if not use_zero_padding:
                    return []
                continue
            
            if response.status_code != 200:
                logger.warning(f"目录页面返回非200状态码 ({format_name}): {response.status_code}")
                if not use_zero_padding:
                    return []
                continue
            
            response.encoding = 'utf-8'
            
            # 提取新闻链接
            news_links = extract_news_links_from_html(response.text, directory_url)
            
            if news_links:
                logger.info(f"从目录页面提取到 {len(news_links)} 个新闻链接 ({format_name})")
                return news_links
            else:
                logger.warning(f"目录页面未找到新闻链接 ({format_name})")
                if not use_zero_padding:
                    return []
                continue
                
        except requests.RequestException as e:
            logger.error(f"访问目录页面失败 ({format_name}): {e}")
            if not use_zero_padding:
                return []
            continue
        except Exception as e:
            logger.error(f"解析目录页面失败 ({format_name}): {e}")
            if not use_zero_padding:
                return []
            continue
    
    return []


def crawl_news_from_directory(date: datetime, skip_existing: bool = True) -> List[Tuple[str, str, datetime]]:
    """
    从目录页面爬取所有新闻
    
    Args:
        date: 日期对象（目录日期）
        skip_existing: 是否跳过已存在的文件（仅返回需要爬取的新闻）
        
    Returns:
        List[Tuple[str, str, datetime]]: 新闻列表 [(标题, 内容, 实际日期), ...]
    """
    # 获取目录页面的所有新闻链接
    news_links = fetch_news_links_from_directory(date)
    
    if not news_links:
        logger.warning(f"目录页面 {date.strftime('%Y-%m-%d')} 未找到新闻链接")
        return []
    
    # 去重：使用URL作为key（去除末尾的斜杠和查询参数）
    seen_urls = set()
    unique_links = []
    for link in news_links:
        # 规范化URL：去除末尾斜杠和查询参数
        normalized = link.rstrip('/').split('?')[0]
        if normalized not in seen_urls:
            seen_urls.add(normalized)
            unique_links.append(link)
    
    logger.info(f"去重后剩余 {len(unique_links)} 个唯一新闻链接（原始: {len(news_links)} 个）")
    
    results = []
    seen_results = set()  # 用于去重（标题+日期）
    
    for link in unique_links:
        # 如果启用跳过已存在文件，先尝试从URL中提取日期进行预检查
        if skip_existing:
            # 尝试从URL路径中提取日期
            url_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', link)
            if url_match:
                try:
                    year, month, day = int(url_match.group(1)), int(url_match.group(2)), int(url_match.group(3))
                    # 尝试多个可能的日期（URL路径日期和可能的实际日期）
                    possible_dates = [datetime(year, month, day)]
                    # 如果URL路径日期与目录日期不同，也检查目录日期
                    if (year, month, day) != (date.year, date.month, date.day):
                        possible_dates.append(date)
                    
                    # 检查是否所有可能的日期都已存在
                    all_exist = all(check_news_file_exists(d) for d in possible_dates)
                    if all_exist:
                        logger.info(f"⏭ 跳过已存在的新闻（预检查）: {link[:80]}...")
                        continue
                except (ValueError, IndexError):
                    pass  # URL解析失败，继续正常流程
        
        logger.info(f"正在爬取新闻: {link}")
        
        # 使用现有的 fetch_news_by_url 函数爬取单个新闻
        result = fetch_news_by_url(link, date=None)  # 不提供日期，让函数从标题提取
        
        if result:
            title, content, actual_date = result
            
            # 如果启用跳过已存在文件，检查实际日期文件是否存在
            if skip_existing and check_news_file_exists(actual_date):
                logger.info(f"⏭ 跳过已存在的新闻: {actual_date.strftime('%Y-%m-%d')} ({title[:50]}...)")
                continue
            
            # 去重：如果标题和日期相同，跳过（避免重复保存）
            result_key = (title, actual_date.strftime('%Y-%m-%d'))
            if result_key not in seen_results:
                seen_results.add(result_key)
                # 同时保留来源链接
                results.append((title, content, actual_date, link))
                logger.info(f"成功爬取: {title} (实际日期: {actual_date.strftime('%Y-%m-%d')})")
            else:
                logger.info(f"跳过重复新闻: {title} (实际日期: {actual_date.strftime('%Y-%m-%d')})")
        else:
            logger.warning(f"爬取失败: {link}")
    
    return results


def check_news_file_exists(date: datetime) -> bool:
    """
    检查指定日期的新闻文件是否已存在
    
    Args:
        date: 日期对象
        
    Returns:
        bool: 文件是否存在
    """
    news_dir = Path(__file__).parent.parent / 'data' / 'news'
    date_str = date.strftime('%Y%m%d')
    file_path = news_dir / f'{date_str}.md'
    return file_path.exists()


def crawl_and_save_from_directory(date: datetime) -> Dict[str, int]:
    """
    从目录页面爬取并保存所有新闻
    
    Args:
        date: 日期对象（目录日期）
        
    Returns:
        Dict[str, int]: 统计信息 {"success": 成功数, "failed": 失败数, "skipped": 跳过数}
    """
    stats = {"success": 0, "failed": 0, "skipped": 0}

    # 检查日期是否为未来日期（新闻联播是历史新闻，不应该爬取未来日期）
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if date > today:
        logger.warning(f"⚠️  日期 {date.strftime('%Y-%m-%d')} 是未来日期，新闻联播尚未播出，无法爬取")
        stats["failed"] = 1
        return stats

    # 如果是今天，检查当前时间是否已过新闻联播时间（晚上 19:00）
    if date == today:
        now = datetime.now()
        broadcast_hour = 19  # 新闻联播播出时间：19:00
        if now.hour < broadcast_hour:
            logger.warning(f"⚠️  当前时间 {now.strftime('%H:%M')} 早于新闻联播时间 {broadcast_hour:02d}:00，新闻联播尚未播出，跳过")
            stats["skipped"] = 1
            return stats

    # 优先直接按日期爬取（使用 govopendata 优先的 fetch_news_by_date）
    if check_news_file_exists(date):
        logger.info(f"⏭ 已存在 {date.strftime('%Y-%m-%d')}，跳过爬取")
        stats["skipped"] = 1
        return stats

    direct_result = fetch_news_by_date(date)
    if direct_result:
        title, content, source_url = direct_result
        file_path = save_news_to_file(title, content, date, source_url=source_url)
        if file_path:
            stats["success"] = 1
            remove_date_from_not_exist(date)
            logger.info(f"✓ 直接爬取成功并保存: {file_path}")
        else:
            stats["failed"] = 1
            logger.error(f"✗ 直接爬取后保存失败: {title}")
        return stats
    
    # 获取目录页面的所有新闻链接
    news_links = fetch_news_links_from_directory(date)
    
    if not news_links:
        logger.warning(f"目录页面 {date.strftime('%Y-%m-%d')} 未找到新闻链接，记录为缺失")
        record_missing_date(date)
        stats["failed"] = 1
        return stats
    
    # 爬取所有新闻（自动跳过已存在的文件）
    news_list = crawl_news_from_directory(date, skip_existing=True)
    
    if not news_list:
        # 检查是否是因为所有文件都已存在而返回空列表
        # 如果目录页面有链接但返回空列表，可能是所有文件都已存在
        # 统计跳过的文件数量（通过检查目录页面中的链接）
        skipped_count = 0
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
            stats["skipped"] = len(news_links)  # 估算跳过的数量
        else:
            logger.warning(f"目录页面 {date.strftime('%Y-%m-%d')} 未能成功爬取任何新闻")
            stats["failed"] = 1
        return stats
    
    # 保存每个新闻（按实际日期）
    # 注意：crawl_news_from_directory 已经过滤了已存在的文件，这里直接保存即可
    for item in news_list:
        # item: (title, content, actual_date, source_link)
        if len(item) == 4:
            title, content, actual_date, source_link = item
        else:
            title, content, actual_date = item
            source_link = None

        file_path = save_news_to_file(title, content, actual_date, source_url=source_link)
        
        if file_path:
            stats["success"] += 1
            logger.info(f"✓ 成功保存: {file_path} (日期: {actual_date.strftime('%Y-%m-%d')})")
        else:
            stats["failed"] += 1
            logger.error(f"✗ 保存失败: {title} (日期: {actual_date.strftime('%Y-%m-%d')})")
    
    return stats


def fetch_news_by_url(url: str, date: datetime = None) -> Optional[Tuple[str, str, datetime]]:
    """
    通过指定URL爬取新闻（用于处理URL不正确的情况）
    
    Args:
        url: 新闻URL
        date: 日期对象（可选，如果为None则尝试从URL或内容中提取）
        
    Returns:
        Tuple[str, str, datetime]: (标题, 格式化后的内容, 日期) 或 None
    """
    logger.info(f"正在通过指定URL爬取: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查404错误
        if response.status_code == 404:
            logger.warning(f"该URL没有新闻: {url}")
            if date:
                record_missing_date(date)
            return None
        
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 获取标题
        title = None
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        # 从标题中提取日期
        extracted_date = None
        if title:
            extracted_date = extract_date_from_title(title)
        
        # 如果提供了日期，使用提供的日期；否则使用提取的日期
        if date:
            final_date = date
        elif extracted_date:
            final_date = extracted_date
        else:
            # 尝试从URL路径中提取日期
            import re
            url_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', url)
            if url_match:
                year, month, day = int(url_match.group(1)), int(url_match.group(2)), int(url_match.group(3))
                final_date = datetime(year, month, day)
            else:
                logger.error("无法确定日期，请手动指定日期")
                return None
        
        if not title:
            title = f"{final_date.strftime('%Y年%m月%d日')}新闻联播文字版"
        
        # 查找正文内容
        content_div = (
            soup.find('div', class_='entry-content') or
            soup.find('div', class_='post-content') or
            soup.find('div', class_='content') or
            soup.find('article') or
            soup.find('div', id='content') or
            soup.find('main')
        )
        
        if not content_div:
            logger.error("未找到文章正文内容")
            return None
        
        # 移除不需要的元素
        for tag in content_div.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # 移除广告和导航链接
        for tag in content_div.find_all(['a'], href=True):
            if tag.parent:
                tag.replace_with(tag.get_text())
        
        # 提取纯文本
        content = content_div.get_text(separator='\n', strip=True)
        
        if not content:
            logger.error("文章内容为空")
            return None
        
        # 格式化内容
        formatted_content = format_news_content(content)
        
        logger.info(f"成功爬取文章，内容长度: {len(formatted_content)} 字符")
        logger.info(f"提取的日期: {final_date.strftime('%Y-%m-%d')}")
        
        return title, formatted_content, final_date
        
    except requests.RequestException as e:
        logger.error(f"网络请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"爬取过程出错: {e}")
        return None


def fetch_news_by_date(date: datetime, retry_count: int = 3) -> Optional[Tuple[str, str, str]]:
    """
    爬取指定日期的新闻，优先从 govopendata 新源获取，失败时回退到 mrxwlb。

    Args:
        date: 日期对象
        retry_count: 重试次数（用于网络错误）

    Returns:
        Tuple[str, str, str]: (标题, 格式化后的内容, source_url) 或 None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
        'Referer': 'https://www.google.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # 先尝试新的 govopendata 源（简洁的 YYYYMMDD 目录），如果成功直接返回
    gov_url = build_govopendata_url(date)
    logger.info(f"优先尝试 govopendata 源: {gov_url}")
    def extract_gov_content(soup: BeautifulSoup) -> Optional[str]:
        """
        从 govopendata 网站提取所有新闻内容
        网站结构：每条新闻是一个 <article> 标签，包含 <h2> 标题和 <p> 段落
        """
        # 首先尝试找到所有 article 元素（govopendata 的特定结构）
        articles = soup.find_all('article')
        
        if articles and len(articles) > 0:
            # 找到了多个新闻条目，逐个提取并格式化
            all_news = []
            
            for idx, article in enumerate(articles, 1):
                # 提取标题 (h2)
                title_elem = article.find('h2')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                # 提取段落内容 (p)
                paragraphs = article.find_all('p')
                if not paragraphs:
                    continue
                    
                # 清理链接，保留文本
                for tag in article.find_all(['a'], href=True):
                    if tag.parent:
                        tag.replace_with(tag.get_text())
                
                # 合并段落内容
                content_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                if not content_parts:
                    continue
                    
                content = '\n\n'.join(content_parts)
                
                # 格式化为 markdown
                news_block = f"## {idx}. {title}\n\n{content}"
                all_news.append(news_block)
            
            if all_news:
                # 用分隔线连接所有新闻
                return '\n\n---\n\n'.join(all_news)
        
        # 如果没有找到 article 元素，使用原来的回退逻辑
        candidates = [
            soup.find('div', class_='entry-content'),
            soup.find('div', class_='post-content'),
            soup.find('div', class_='content'),
            soup.find('div', id='content'),
            soup.find('main'),
            soup.find('section', role='main'),
            soup.find('section', class_='content'),
            soup.find('div', class_=lambda x: x and 'post' in ' '.join(x)),
        ]

        # 过滤掉 None
        candidates = [c for c in candidates if c]

        # 追加一个回退：如果前面都失败，尝试 body
        if soup.body:
            candidates.append(soup.body)

        for block in candidates:
            # 清理无关元素
            for tag in block.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            for tag in block.find_all(['a'], href=True):
                if tag.parent:
                    tag.replace_with(tag.get_text())

            text = block.get_text(separator='\n', strip=True)
            if text and len(text.strip()) >= 50:
                return text
        return None

    try:
        import time
        time.sleep(0.5)  # 添加小延迟，避免被检测为机器爬虫
        resp = requests.get(gov_url, headers=headers, timeout=12)
        if resp.status_code == 200:
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'lxml')
            title = None
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)

            if not title:
                title = f"{date.strftime('%Y年%m月%d日')}新闻联播文字版"

            content = extract_gov_content(soup)

            if content:
                formatted_content = format_news_content(content)
                logger.info(f"成功从 govopendata 源爬取: {gov_url}")
                return title, formatted_content, gov_url
            else:
                logger.warning(f"govopendata 未找到正文或内容过短: {gov_url}")
        else:
            logger.info(f"govopendata 返回状态: {resp.status_code} -> {gov_url}")
            
            # 如果是 403（反爬虫），尝试使用 Selenium
            if resp.status_code == 403:
                logger.info(f"遇到 403 反爬虫，尝试使用 Selenium...")
                from src.utils.browser_helper import fetch_with_selenium
                try:
                    html = fetch_with_selenium(gov_url, timeout=15)
                    if html:
                        soup = BeautifulSoup(html, 'lxml')
                        
                        title = None
                        title_elem = soup.find('h1') or soup.find('title')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                        
                        if not title:
                            title = f"{date.strftime('%Y年%m月%d日')}新闻联播文字版"
                        
                        content = extract_gov_content(soup)
                        
                        if content:
                            formatted_content = format_news_content(content)
                            logger.info(f"✓ 使用 Selenium 成功从 govopendata 源爬取: {gov_url}")
                            return title, formatted_content, gov_url
                except Exception as e:
                    logger.warning(f"Selenium 尝试失败: {e}")
                    
    except requests.RequestException as e:
        logger.warning(f"访问 govopendata 源失败: {e}")

    # 尝试两种URL格式：先尝试两位数格式，如果404再尝试个位数格式
    url_formats = [
        (True, "两位数格式"),   # 01/07
        (False, "个位数格式"),  # 1/7
    ]
    
    for use_zero_padding, format_name in url_formats:
        url = build_news_url(date, use_zero_padding=use_zero_padding)
        logger.info(f"正在爬取 ({format_name}): {url}")
        
        # 重试逻辑
        for attempt in range(retry_count):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                
                # 检查404错误
                if response.status_code == 404:
                    # 如果是第一个格式（两位数）返回404，尝试第二个格式（个位数）
                    if use_zero_padding:
                        logger.info(f"两位数格式返回404，尝试个位数格式...")
                        break  # 跳出内层循环，尝试下一个URL格式
                    else:
                        # 两种格式都404，记录为缺失
                        logger.warning(f"该日期没有新闻（两种格式都404）: {date.strftime('%Y-%m-%d')}")
                        record_missing_date(date)
                        return None
            
                # 其他HTTP错误，记录但不标记为缺失（可能是临时错误）
                if response.status_code != 200:
                    logger.warning(f"HTTP错误 {response.status_code}，URL: {url}")
                    if attempt < retry_count - 1:
                        logger.info(f"重试中... ({attempt + 1}/{retry_count})")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        # 如果当前格式失败，尝试下一个格式
                        if use_zero_padding:
                            logger.info(f"两位数格式失败，尝试个位数格式...")
                            break  # 跳出内层循环，尝试下一个URL格式
                        else:
                            logger.error(f"重试{retry_count}次后仍失败")
                            return None
                
                # 成功获取响应，处理内容
                response.encoding = 'utf-8'
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # 获取标题
                title = None
                title_elem = soup.find('h1') or soup.find('title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                
                if not title:
                    # 从URL构建标题
                    title = f"{date.strftime('%Y年%m月%d日')}新闻联播文字版"
                
                # 查找正文内容 - 尝试多种选择器
                content_div = (
                    soup.find('div', class_='entry-content') or
                    soup.find('div', class_='post-content') or
                    soup.find('div', class_='content') or
                    soup.find('article') or
                    soup.find('div', id='content') or
                    soup.find('main') or
                    soup.find('div', class_=lambda x: x and 'content' in ' '.join(x).lower()) or
                    soup.find('div', id=lambda x: x and 'content' in x.lower() if x else False)
                )
                
                if not content_div:
                    logger.error(f"未找到文章正文内容，URL: {url}")
                    logger.debug(f"页面标题: {soup.find('title').get_text() if soup.find('title') else 'N/A'}")
                    # 如果当前格式失败，尝试下一个格式
                    if use_zero_padding:
                        logger.info(f"两位数格式未找到内容，尝试个位数格式...")
                        break  # 跳出内层循环，尝试下一个URL格式
                    else:
                        # 不记录为缺失，因为可能是页面结构变化
                        return None
                
                # 移除不需要的元素
                for tag in content_div.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    tag.decompose()
                
                # 移除广告和导航链接
                for tag in content_div.find_all(['a'], href=True):
                    # 保留文本，移除链接
                    if tag.parent:
                        tag.replace_with(tag.get_text())
                
                # 提取纯文本
                content = content_div.get_text(separator='\n', strip=True)
                
                if not content or len(content.strip()) < 50:
                    logger.error(f"文章内容为空或过短，URL: {url}, 内容长度: {len(content) if content else 0}")
                    # 如果当前格式失败，尝试下一个格式
                    if use_zero_padding:
                        logger.info(f"两位数格式内容过短，尝试个位数格式...")
                        break  # 跳出内层循环，尝试下一个URL格式
                    else:
                        # 不记录为缺失，因为可能是页面结构变化
                        return None
                
                # 格式化内容
                formatted_content = format_news_content(content)
                
                logger.info(f"成功爬取文章（使用{format_name}），内容长度: {len(formatted_content)} 字符")
                # 返回时附带实际使用的来源 URL（mrxwlb）
                return title, formatted_content, url
                
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，URL: {url}")
                if attempt < retry_count - 1:
                    logger.info(f"重试中... ({attempt + 1}/{retry_count})")
                    import time
                    time.sleep(2)
                    continue
                else:
                    # 如果当前格式超时，尝试下一个格式
                    if use_zero_padding:
                        logger.info(f"两位数格式超时，尝试个位数格式...")
                        break  # 跳出内层循环，尝试下一个URL格式
                    else:
                        logger.error(f"重试{retry_count}次后仍超时")
                        return None
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"连接错误，URL: {url}")
                if attempt < retry_count - 1:
                    logger.info(f"重试中... ({attempt + 1}/{retry_count})")
                    import time
                    time.sleep(2)
                    continue
                else:
                    # 如果当前格式连接失败，尝试下一个格式
                    if use_zero_padding:
                        logger.info(f"两位数格式连接失败，尝试个位数格式...")
                        break  # 跳出内层循环，尝试下一个URL格式
                    else:
                        logger.error(f"重试{retry_count}次后仍连接失败")
                        return None
                    
            except requests.RequestException as e:
                logger.error(f"网络请求失败: {e}, URL: {url}")
                if attempt < retry_count - 1:
                    logger.info(f"重试中... ({attempt + 1}/{retry_count})")
                    import time
                    time.sleep(2)
                    continue
                else:
                    # 如果当前格式失败，尝试下一个格式
                    if use_zero_padding:
                        logger.info(f"两位数格式请求失败，尝试个位数格式...")
                        break  # 跳出内层循环，尝试下一个URL格式
                    else:
                        return None
                    
            except Exception as e:
                logger.error(f"爬取过程出错: {e}, URL: {url}")
                logger.exception(e)  # 打印详细错误信息
                # 如果当前格式出错，尝试下一个格式
                if use_zero_padding:
                    logger.info(f"两位数格式出错，尝试个位数格式...")
                    break  # 跳出内层循环，尝试下一个URL格式
                else:
                    return None
        
        # 如果当前格式成功，直接返回（不会执行到这里）
        # 如果当前格式失败且不是最后一个格式，继续尝试下一个格式
    
    # 所有格式都尝试失败
    logger.error(f"所有URL格式都尝试失败: {date.strftime('%Y-%m-%d')}")
    return None


def save_news_to_file(title: str, content: str, date: datetime, source_url: str = None) -> Optional[str]:
    """
    将新闻保存到文件
    
    Args:
        title: 新闻标题
        content: 格式化后的内容
        date: 日期对象
        
    Returns:
        str: 保存的文件路径，或 None
    """
    try:
        # 创建保存目录
        news_dir = Path(__file__).parent.parent / 'data' / 'news'
        news_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名：YYYYMMDD.md
        date_str = date.strftime('%Y%m%d')
        file_path = news_dir / f'{date_str}.md'
        
        # 构建 Markdown 内容并记录来源 URL
        recorded_source = source_url if source_url else build_news_url(date)
        source_domain = urlparse(recorded_source).netloc if recorded_source else ''
        # 构建 Markdown 内容
        markdown_content = f"""# {date.strftime('%Y年%m月%d日')} 新闻联播

**日期**: {date.strftime('%Y年%m月%d日')}  
**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}

---

*来源: {source_domain}*  
*URL: {recorded_source}*
"""
        
        # 保存文件
        file_path.write_text(markdown_content, encoding='utf-8')
        logger.info(f"新闻已保存到: {file_path}")
        
        return str(file_path)
        
    except Exception as e:
        logger.error(f"保存新闻文件失败: {e}")
        return None


def record_missing_date(date: datetime) -> None:
    """
    记录缺失的日期到 not_exist.md 文件（使用累加更新方式）
    
    Args:
        date: 缺失新闻的日期
    """
    # 直接调用 update_not_exist_file 函数，保持格式一致
    update_not_exist_file([date])


def remove_date_from_not_exist(date: datetime) -> None:
    """
    从 not_exist.md 文件中移除指定日期（当该日期成功爬取后调用）

    Args:
        date: 要移除的日期
    """
    try:
        data_dir = Path(__file__).parent.parent / 'data' / 'news'
        not_exist_file = data_dir / 'not_exist.md'

        if not not_exist_file.exists():
            return

        # 读取现有内容
        existing_content = not_exist_file.read_text(encoding='utf-8')

        # 提取所有日期
        import re
        date_matches = re.findall(r'- (\d{4}-\d{2}-\d{2})', existing_content)
        all_dates = []
        for date_str in date_matches:
            try:
                all_dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
            except ValueError:
                pass

        # 移除指定日期
        date_str = date.strftime('%Y-%m-%d')
        all_dates = [d for d in all_dates if d.strftime('%Y-%m-%d') != date_str]

        # 如果没有变化，直接返回
        if len(all_dates) == len(date_matches):
            return

        # 去重并排序
        all_dates = sorted(set(all_dates))

        # 生成新内容
        content = """# 缺失的新闻日期

本文档记录所有未找到新闻的日期。

**更新时间**: {update_time}

## 缺失日期列表

""".format(update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # 按月份分组
        current_month = None
        for d in all_dates:
            date_str_cn = d.strftime('%Y年%m月%d日')
            month_str = d.strftime('%Y年%m月')

            if current_month != month_str:
                if current_month is not None:
                    content += "\n"
                content += f"### {month_str}\n\n"
                current_month = month_str

            content += f"- {d.strftime('%Y-%m-%d')} ({date_str_cn})\n"

        content += "\n---\n"
        content += f"\n**总计**: {len(all_dates)} 个日期缺失新闻\n"

        # 写入文件
        not_exist_file.write_text(content, encoding='utf-8')
        logger.info(f"已从缺失日期文件中移除: {date_str}")

    except Exception as e:
        logger.error(f"移除缺失日期失败: {e}")


def update_not_exist_file(dates: List[datetime]) -> None:
    """
    更新 not_exist.md 文件，累加缺失的日期（不覆盖已有数据）
    
    Args:
        dates: 本次新增的缺失新闻日期列表
    """
    try:
        data_dir = Path(__file__).parent.parent / 'data' / 'news'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        not_exist_file = data_dir / 'not_exist.md'
        
        if not dates:
            return
        
        # 读取现有日期
        existing_dates = set()
        existing_content = ""
        
        if not_exist_file.exists():
            existing_content = not_exist_file.read_text(encoding='utf-8')
            # 提取已有日期
            import re
            date_matches = re.findall(r'- (\d{4}-\d{2}-\d{2})', existing_content)
            existing_dates = set(date_matches)
        
        # 过滤出新增的日期
        new_dates = []
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in existing_dates:
                new_dates.append(date)
                existing_dates.add(date_str)
        
        if not new_dates:
            logger.info("没有新的缺失日期需要添加")
            return
        
        # 合并所有日期（包括已有的和新添加的）
        all_dates = []
        
        # 从现有内容中提取日期
        if existing_content:
            import re
            date_matches = re.findall(r'- (\d{4}-\d{2}-\d{2})', existing_content)
            for date_str in date_matches:
                try:
                    all_dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                except ValueError:
                    pass
        
        # 添加新日期
        all_dates.extend(new_dates)
        
        # 去重并排序
        all_dates = sorted(set(all_dates))
        
        # 生成新内容
        content = """# 缺失的新闻日期

本文档记录所有未找到新闻的日期。

**更新时间**: {update_time}

## 缺失日期列表

""".format(update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 按月份分组
        current_month = None
        for date in all_dates:
            date_str = date.strftime('%Y-%m-%d')
            date_str_cn = date.strftime('%Y年%m月%d日')
            month_str = date.strftime('%Y年%m月')
            
            if current_month != month_str:
                if current_month is not None:
                    content += "\n"
                content += f"### {month_str}\n\n"
                current_month = month_str
            
            content += f"- {date_str} ({date_str_cn})\n"
        
        content += "\n---\n"
        content += f"\n**总计**: {len(all_dates)} 个日期缺失新闻\n"
        
        # 写入文件
        not_exist_file.write_text(content, encoding='utf-8')
        logger.info(f"已更新缺失日期文件: {not_exist_file}, 新增 {len(new_dates)} 个日期，总计 {len(all_dates)} 个日期")
        
    except Exception as e:
        logger.error(f"更新缺失日期文件失败: {e}")


def crawl_and_save(date: datetime = None) -> Optional[str]:
    """
    爬取并保存新闻（便捷函数）
    
    Args:
        date: 日期对象，如果为 None 则使用当前日期
        
    Returns:
        str: 保存的文件路径，或 None
    """
    if date is None:
        date = datetime.now()
    
    # 爬取新闻
    result = fetch_news_by_date(date)
    if not result:
        return None

    # fetch_news_by_date 返回 (title, content, source_url)
    title, content, source_url = result

    # 保存文件并记录来源
    return save_news_to_file(title, content, date, source_url=source_url)

