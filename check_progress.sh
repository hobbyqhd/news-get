#!/bin/bash
# 检查爬取进度脚本

cd "$(dirname "$0")"

echo "=== 爬取任务进度检查 ==="
echo ""

# 检查正在运行的任务
echo "正在运行的任务:"
ps aux | grep "[c]rawl_news.py" | awk '{print "  PID:", $2, "| 命令:", substr($0, index($0,$11))}'
echo ""

# 统计各年份文件数
echo "=== 已爬取文件统计 ==="
for year in 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025; do
    count=$(ls -1 data/news/${year}*.md 2>/dev/null | grep -v not_exist.md | wc -l | tr -d ' ')
    if [ "$count" != "0" ] || [ -n "$(ls -1 data/news/${year}*.md 2>/dev/null | grep -v not_exist.md)" ]; then
        echo "${year}年: ${count} 个文件"
    fi
done
echo ""

# 检查各个任务的日志
for log_file in crawl_2016_2019.log crawl_2020_2024.log crawl_2025.log; do
    if [ -f "$log_file" ]; then
        year_range=$(echo "$log_file" | sed 's/crawl_//;s/.log//')
        echo "=== ${year_range} 任务进度 ==="
        tail -3 "$log_file" | grep "处理日期" | tail -1
        success_count=$(grep -c "✓ 成功" "$log_file" 2>/dev/null || echo "0")
        fail_count=$(grep -c "✗ 失败" "$log_file" 2>/dev/null || echo "0")
        echo "  成功: ${success_count} | 失败: ${fail_count}"
        echo ""
    fi
done

# 统计缺失日期
if [ -f data/news/not_exist.md ]; then
    echo "=== 缺失日期统计 ==="
    grep "总计" data/news/not_exist.md | head -1
    echo ""
fi

echo "=== 查看实时日志 ==="
echo "2016-2019年: tail -f crawl_2016_2019.log"
echo "2020-2024年: tail -f crawl_2020_2024.log"
echo "2025年: tail -f crawl_2025.log"
echo ""

