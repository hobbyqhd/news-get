#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并所有月份新闻的脚本"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 设置路径
base_path = Path("/Users/lmc10278/Library/Mobile Documents/com~apple~CloudDocs/Code/github/hobbyqhd/news-get")
news_dir = base_path / "data" / "news"
reports_dir = base_path / "data" / "reports"

# 创建reports目录
reports_dir.mkdir(parents=True, exist_ok=True)

# 按月份分组文件
monthly_files = defaultdict(list)
all_files = sorted(news_dir.glob("[0-9][0-9][0-9][0-9][0-9][0-9]*.md"))

print(f"找到 {len(all_files)} 个新闻文件")

for file_path in all_files:
    # 提取年月信息：20260101.md -> 202601
    date_str = file_path.stem[:6]
    monthly_files[date_str].append(file_path)

print(f"按月份分组：{len(monthly_files)} 个月份")
print()

# 为每个月创建汇总文件
for month in sorted(monthly_files.keys()):
    files = monthly_files[month]
    
    # 转换月份格式：202601 -> 2026-01
    year = month[:4]
    month_num = month[4:6]
    formatted_month = f"{year}-{month_num}"
    
    # 创建文件名
    output_file = reports_dir / f"{year}年{month_num}月新闻汇总.md"
    
    print(f"[{month}] 整合 {len(files)} 个文件 → {output_file.name}")
    
    # 创建整合文档
    content = []
    content.append(f"# {year}年{month_num}月新闻汇总\n\n")
    content.append(f"整理时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append(f"总计新闻日期：{len(files)} 天\n\n")
    content.append("---\n")
    
    # 逐个读取和整合文件
    for i, file_path in enumerate(files, 1):
        date_str = file_path.stem  # 20260101
        # 转换日期格式：20260101 -> 2026-01-01
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # 添加日期标题
            content.append(f"\n## {formatted_date}\n\n")
            content.append(file_content)
            content.append("\n\n---\n")
        except Exception as e:
            print(f"    ✗ 错误读取 {file_path.name}: {e}")
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("".join(content))
        size_kb = output_file.stat().st_size / 1024
        print(f"  ✓ 完成 ({size_kb:.1f} KB)\n")
    except Exception as e:
        print(f"  ✗ 错误写入: {e}\n")

print("=" * 60)
print("✓ 所有月份新闻汇总完成！")
print(f"✓ 输出目录: {reports_dir}")
print(f"✓ 总计生成: {len(monthly_files)} 个汇总文件")
