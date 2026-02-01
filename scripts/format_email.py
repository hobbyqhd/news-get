#!/usr/bin/env python3
"""
Format email body from new markdown files.
Reads from data/new_files.txt and creates HTML email body.
Outputs EMAIL_BODY environment variable.
"""

import os
import glob
from pathlib import Path

def get_new_files_list():
    """Get list of new markdown files to include in email."""
    new_files_path = Path("data/new_files.txt")
    new_files = []
    
    if new_files_path.exists():
        with open(new_files_path, 'r', encoding='utf-8') as f:
            for line in f:
                file_path = line.strip()
                if file_path and file_path.endswith('.md'):
                    new_files.append(file_path)
    
    return new_files

def get_file_content(file_path):
    """Read markdown file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Limit content to first 500 characters to avoid email being too long
            return content[:500] if len(content) > 500 else content
    except Exception as e:
        return f"Error reading file: {e}"

def format_email_body():
    """Format HTML email body with new files."""
    new_files = get_new_files_list()
    
    if not new_files:
        return "<p>No new files found.</p>"
    
    html_body = """<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .file-item { margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #2196F3; }
        .file-name { font-weight: bold; font-size: 1.1em; color: #2196F3; }
        .file-content { margin-top: 10px; white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <h2>📰 每日新闻更新</h2>
    <p>以下是今日新增的新闻内容：</p>
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
    <hr>
    <p><small>此邮件由自动化爬虫生成</small></p>
</body>
</html>"""
    
    return html_body

def main():
    """Main function to generate and output email body."""
    email_body = format_email_body()
    
    # Write to environment variable file
    with open(os.environ.get('GITHUB_ENV', '/tmp/github_env'), 'a', encoding='utf-8') as f:
        # Escape newlines for GitHub environment variable
        escaped_body = email_body.replace('\n', '%0A').replace('%', '%25')
        f.write(f"EMAIL_BODY={escaped_body}\n")
    
    print("Email body formatted successfully!")

if __name__ == "__main__":
    main()
