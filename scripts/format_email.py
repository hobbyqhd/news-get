#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成格式化的邮件 HTML 正文
"""

import re
import os
import sys

def escape_html(text):
    """HTML 转义"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def format_markdown_to_html(content):
    """简单的 Markdown 到 HTML 转换"""
    # 处理代码块
    content = re.sub(
        r'```[\s\S]*?```',
        lambda m: '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">' + escape_html(m.group(0)) + '</pre>',
        content
    )
    
    # 处理加粗
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'__(.*?)__', r'<strong>\1</strong>', content)
    
    # 处理斜体
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    content = re.sub(r'_(.*?)_', r'<em>\1</em>', content)
    
    # 处理标题
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    
    # 处理列表
    content = re.sub(r'^- (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'^(\d+)\. (.*?)$', r'<li>\2</li>', content, flags=re.MULTILINE)
    
    # 包装列表项
    content = re.sub(r'(<li>.*?</li>)', lambda m: '<ul>' + m.group(1) + '</ul>', content)
    
    # 处理段落 - 跳过已有的 HTML 标签
    lines = content.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<'):
            result.append('<p>' + line + '</p>')
        elif line:
            result.append(line)
    content = '\n'.join(result)
    
    return content

def main():
    # HTML 基础样式
    html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body {{ 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; 
        line-height: 1.6; 
        margin: 0; 
        padding: 0; 
        background-color: #f9f9f9;
        color: #333;
      }}
      .container {{ 
        max-width: 600px; 
        margin: 0 auto; 
        padding: 20px;
        background-color: #ffffff;
      }}
      .header {{ 
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 3px solid #007bff;
        padding-bottom: 20px;
      }}
      .header h1 {{
        color: #007bff;
        margin: 0 0 10px 0;
        font-size: 24px;
      }}
      .header p {{
        color: #666;
        margin: 5px 0;
        font-size: 14px;
      }}
      .news-item {{ 
        background: #f0f7ff; 
        padding: 20px; 
        margin: 20px 0; 
        border-radius: 8px;
        border-left: 5px solid #007bff; 
      }}
      .news-date {{ 
        color: #007bff; 
        font-weight: bold; 
        margin-bottom: 15px;
        font-size: 16px;
      }}
      .news-content {{ 
        color: #333; 
        font-size: 14px;
        line-height: 1.8;
      }}
      .news-content h2 {{
        color: #007bff;
        font-size: 16px;
        margin: 12px 0 8px 0;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 6px;
      }}
      .news-content h3 {{
        color: #0056b3;
        font-size: 14px;
        margin: 10px 0 5px 0;
      }}
      .news-content ul, .news-content ol {{
        margin: 8px 0;
        padding-left: 20px;
      }}
      .news-content li {{
        margin: 6px 0;
      }}
      .news-content p {{
        margin: 8px 0;
      }}
      .news-content strong {{
        color: #007bff;
      }}
      .divider {{
        height: 1px;
        background-color: #ddd;
        margin: 20px 0;
      }}
      .footer {{ 
        margin-top: 30px; 
        padding-top: 20px;
        border-top: 1px solid #ddd;
        color: #999; 
        font-size: 12px; 
        text-align: center;
      }}
    </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📰 每日新闻更新</h1>
      <p>亲爱的用户，以下是今日新生成的新闻内容</p>
    </div>
{content}
    <div class="footer">
      <p>感谢您的关注！<br>此邮件由 GitHub Actions 自动生成</p>
    </div>
  </div>
</body>
</html>"""
    
    # 检查是否有新文件
    if not os.path.exists('data/new_files.txt') or os.path.getsize('data/new_files.txt') == 0:
        print("No new files found")
        email_body = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body><p>今日未新增新闻内容。</p></body>
</html>"""
        # 写入环境变量
        github_env = os.environ.get('GITHUB_ENV')
        if github_env:
            with open(github_env, 'a', encoding='utf-8') as f:
                f.write(f"EMAIL_BODY<<ENDOF\n{email_body}\nENDOF\n")
        return
    
    # 读取文件列表
    with open('data/new_files.txt', 'r', encoding='utf-8') as f:
        files = [line.strip() for line in f if line.strip()]
    
    # 按日期排序（倒序，最新的在前），并只取前 3 个
    files.sort(reverse=True)
    files = files[:3]
    
    # 生成新闻内容 HTML
    news_content = ""
    for file_path in files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            date_part = os.path.basename(file_path).replace('.md', '')
            
            # 格式化内容
            formatted_content = format_markdown_to_html(content)
            
            news_content += f'''    <div class="news-item">
      <div class="news-date">📅 {date_part}</div>
      <div class="news-content">
{formatted_content}
      </div>
    </div>
    <div class="divider"></div>
'''
    
    # 生成最终 HTML
    html_body = html_template.format(content=news_content)
    
    # 统计包含的天数
    days_count = len(files)
    print(f"✓ Email body prepared with {days_count} day(s) of news (max 3 days)")
    
    # 写入环境变量文件
    github_env = os.environ.get('GITHUB_ENV')
    if github_env:
        with open(github_env, 'a', encoding='utf-8') as f:
            f.write(f"EMAIL_BODY<<ENDOF\n{html_body}\nENDOF\n")
        print("✓ Email body prepared with formatted MD content")
    else:
        print(html_body)

if __name__ == '__main__':
    main()
