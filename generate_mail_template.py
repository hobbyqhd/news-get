#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件模板生成脚本 - 将新闻数据转换为易读的 HTML 邮件格式
"""

import re
from datetime import datetime
from pathlib import Path

def truncate_text(text, max_length=300):
    """截断文本到指定长度"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def parse_news_file(file_path):
    """从 Markdown 文件解析新闻内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题和元数据
    lines = content.split('\n')
    title = lines[0].replace('# ', '').strip()  # 第一行是大标题
    
    date_match = re.search(r'\*\*日期\*\*:\s*(.+?)\n', content)
    date = date_match.group(1) if date_match else "未知"
    
    source_match = re.search(r'\[(.+?)\]\((.+?)\)', content)
    source_url = source_match.group(2) if source_match else ""
    
    crawl_time_match = re.search(r'\*\*爬取时间\*\*:\s*(.+?)\n', content)
    crawl_time = crawl_time_match.group(1) if crawl_time_match else "未知"
    
    # 提取各新闻项
    news_items = []
    news_sections = re.split(r'## \d+\.\s+', content)
    
    for idx, section in enumerate(news_sections[1:], 1):  # 跳过第一部分
        lines = section.split('\n', 1)
        if len(lines) >= 2:
            news_title = lines[0].strip()
            news_content = lines[1].strip()
            
            # 只取前 300 字符的摘要
            summary = truncate_text(news_content, 280)
            
            news_items.append({
                'number': idx,
                'title': news_title,
                'content': summary,
                'full_content': news_content
            })
    
    return {
        'title': title,
        'date': date.split('(')[0].strip() if '(' in date else date,
        'date_full': date,
        'source_url': source_url,
        'crawl_time': crawl_time,
        'news_items': news_items
    }

def generate_news_html(news_data):
    """生成新闻项的 HTML 代码"""
    html_items = []
    
    for item in news_data['news_items']:
        html = f'''            <div class="news-item">
                <div style="display: flex; align-items: flex-start;">
                    <span class="news-number">{item['number']}</span>
                    <div style="flex: 1;">
                        <div class="news-title">{item['title']}</div>
                        <div class="news-content">{item['content']}</div>
                    </div>
                </div>
            </div>
'''
        html_items.append(html)
    
    return '\n'.join(html_items)

def generate_email(news_data, template_path='mail_template_new.html'):
    """生成完整的邮件 HTML"""
    
    # 读取模板
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 生成新闻项 HTML
    news_html = generate_news_html(news_data)
    
    # 替换模板中的占位符
    email_html = template.replace('{DATE}', news_data['date'])
    email_html = email_html.replace('{CRAWL_TIME}', news_data['crawl_time'])
    email_html = email_html.replace('{SOURCE_URL}', news_data['source_url'])
    email_html = email_html.replace('{NEWS_ITEMS}', news_html)
    
    return email_html

def save_email(email_html, output_path):
    """保存邮件 HTML 到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(email_html)

if __name__ == '__main__':
    # 示例：处理 20260221.md
    news_file = 'data/news/20260221.md'
    template_file = 'mail_template_new.html'
    output_file = 'mail_output_sample.html'
    
    # 检查文件是否存在
    if not Path(news_file).exists():
        print(f"❌ 新闻文件不存在: {news_file}")
        exit(1)
    
    if not Path(template_file).exists():
        print(f"❌ 模板文件不存在: {template_file}")
        exit(1)
    
    # 解析新闻内容
    print(f"📖 正在解析新闻文件: {news_file}")
    news_data = parse_news_file(news_file)
    
    # 生成邮件
    print(f"✍️  正在生成邮件 HTML...")
    email_html = generate_email(news_data, template_file)
    
    # 保存输出
    save_email(email_html, output_file)
    print(f"✅ 邮件已生成: {output_file}")
    
    # 打印统计信息
    print(f"\n📊 统计信息:")
    print(f"   - 日期: {news_data['date']}")
    print(f"   - 新闻项数: {len(news_data['news_items'])}")
    print(f"   - 爬取时间: {news_data['crawl_time']}")
    print(f"   - 来源: {news_data['source_url']}")
