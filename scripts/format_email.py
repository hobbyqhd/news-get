#!/usr/bin/env python3
"""Build HTML email body from newly crawled markdown files."""

import os
from datetime import datetime
from pathlib import Path

def get_new_files_list():
    """Get list of new markdown files from data/new_files.txt."""
    new_files_path = Path("data/new_files.txt")
    new_files = []
    
    if new_files_path.exists():
        with open(new_files_path, 'r', encoding='utf-8') as f:
            for line in f:
                file_path = line.strip()
                if not file_path or not file_path.endswith('.md'):
                    continue

                path_obj = Path(file_path)
                if path_obj.exists():
                    new_files.append(str(path_obj))
                    continue

                fallback = Path("data/news") / path_obj.name
                if fallback.exists():
                    new_files.append(str(fallback))
    
    return new_files

def get_file_content(file_path):
    """Read markdown file content and trim size for email readability."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[:1200] + "..." if len(content) > 1200 else content
    except Exception as e:
        return f"Error reading file: {e}"

def format_email_body():
    """Format modern HTML email body with new files."""
    new_files = get_new_files_list()
    
    if not new_files:
        return "<p>No new files found.</p>"
    
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M")
    html_body = f"""<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; line-height: 1.7; color: #333; background: #f5f7fb; padding: 16px; }}
        .container {{ max-width: 720px; margin: 0 auto; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.08); }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; padding: 22px; }}
        .title {{ margin: 0; font-size: 22px; font-weight: 700; }}
        .sub {{ margin-top: 6px; font-size: 13px; opacity: .9; }}
        .meta {{ padding: 12px 20px; font-size: 12px; color: #666; background: #fafafa; border-bottom: 1px solid #eee; }}
        .content {{ padding: 20px; }}
        .file-item {{ margin-bottom: 14px; padding: 14px; background: #f7f9fc; border: 1px solid #e9eef7; border-radius: 8px; }}
        .file-name {{ font-weight: 700; font-size: 15px; color: #4257b2; margin-bottom: 8px; }}
        .file-content {{ white-space: pre-wrap; word-wrap: break-word; font-size: 13px; color: #444; }}
        .footer {{ padding: 14px 20px 20px; font-size: 12px; color: #888; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
      <div class="header">
        <h2 class="title">📰 每日新闻更新</h2>
        <div class="sub">以下是本次新增的新闻内容</div>
      </div>
      <div class="meta">生成时间：{now_text} ｜ 文件数量：{len(new_files)}</div>
      <div class="content">
"""
    
    for file_path in new_files[:5]:  # Limit to 5 files in email to keep it reasonable size
        file_name = os.path.basename(file_path)
        content = get_file_content(file_path)
        
        # Escape HTML characters
        content_escaped = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        html_body += f"""
        <div class="file-item">
            <div class="file-name">📄 {file_name}</div>
            <div class="file-content">{content_escaped}</div>
        </div>
"""
    
        html_body += """
            </div>
            <div class="footer">此邮件由自动化爬虫生成</div>
        </div>
</body>
</html>"""
    
    return html_body

def main():
    """Generate and export EMAIL_BODY for GitHub Actions."""
    email_body = format_email_body()
    
    github_env = os.environ.get('GITHUB_ENV', '/tmp/github_env')
    with open(github_env, 'a', encoding='utf-8') as f:
        f.write("EMAIL_BODY<<__EMAIL_BODY__\n")
        f.write(email_body)
        f.write("\n__EMAIL_BODY__\n")
    
    print("Email body formatted successfully!")

if __name__ == "__main__":
    main()
