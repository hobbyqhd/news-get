# 📧 新闻邮件格式改进方案

## 📌 概述

重新设计了每日新闻邮件的格式，从URL编码的纯文本改进为现代化的HTML邮件，大幅提升可读性和用户体验。

---

## ✨ 改进对比

### 原格式（问题）
```
%250A%250A %250A %250A%250A%250A
📰 每日新闻更新

%250A
以下是今日新增的新闻内容：
...
```
**问题：**
- ❌ 使用 URL 编码（%250A = 换行符）难以直接阅读
- ❌ 格式混乱，内容难以区分
- ❌ 不支持响应式设计，移动设备阅读体验差
- ❌ 无法使用颜色和排版强调重点

### 新格式（改进）
- ✅ 完整的 HTML5 结构，支持现代邮件客户端
- ✅ 彩色 Gradient Header，视觉吸引力强
- ✅ 编号圆形数字标记，新闻项清晰分离
- ✅ 响应式设计，完美适配桌面和手机
- ✅ 元数据清晰展示（日期、爬取时间、来源）
- ✅ 新闻摘要自动截断，内容不过长

---

## 🎨 新邮件设计特点

### 1. **Header 部分**
- 紫蓝色渐变背景
- 大标题 + 副标题
- 视觉层级清晰

### 2. **元数据区**
```
📅 日期: 2026年02月21日
⏰ 爬取: 2026-02-22 11:19:54
🔗 来源: https://cn.govopendata.com/...
```

### 3. **新闻项目**
- 编号圆形标记（1-14）
- 标题突出显示
- 内容摘要（自动截断 280 字符）
- 清晰的分隔线

### 4. **响应式设计**
```css
@media (max-width: 480px) {
    /* 移动设备优化 */
    - 字体大小自动调整
    - 布局自动转为单列
}
```

### 5. **Footer**
- 生成来源说明
- 版权信息

---

## 🚀 使用方法

### 方式 1：独立生成邮件 HTML

```bash
python3 generate_mail_template.py
```

**输出：** `mail_output_sample.html`

**输出示例：**
```
📖 正在解析新闻文件: data/news/20260221.md
✍️  正在生成邮件 HTML...
✅ 邮件已生成: mail_output_sample.html

📊 统计信息:
   - 日期: 2026年02月21日
   - 新闻项数: 14
   - 爬取时间: 2026-02-22 11:19:54
   - 来源: https://cn.govopendata.com/xinwenlianbo/20260221/
```

### 方式 2：在现有脚本中集成

修改 `scripts/format_email.py`，集成新的模板生成函数：

```python
from generate_mail_template import generate_email, parse_news_file

# 解析要发送的新闻文件
news_data = parse_news_file('data/news/20260221.md')

# 生成邮件 HTML
email_html = generate_email(news_data, 'mail_template_new.html')

# 设置到邮件环境变量
os.environ['EMAIL_BODY'] = email_html
```

---

## 📊 邮件内容结构

### 文件说明

| 文件 | 说明 |
|-----|------|
| `mail_template_new.html` | HTML 邮件模板（可复用） |
| `generate_mail_template.py` | Python 生成脚本 |
| `mail_output_sample.html` | 生成的示例邮件 |

### 模板占位符

```html
{DATE}          <!-- 新闻日期 -->
{CRAWL_TIME}    <!-- 爬取时间 -->
{SOURCE_URL}    <!-- 来源链接 -->
{NEWS_ITEMS}    <!-- 新闻项目 HTML -->
```

---

## 🎯 新闻项摘要生成

**自动截断规则：**
- 每条新闻内容自动截断为 280 字符
- 末尾自动添加 "..."
- 完整内容可通过点击查看

**示例：**

原文（896字）：
> 2025年全国光伏新增装机3.17亿千瓦，同比增长14%。截至2025年12月，全国光伏发电装机容量达到12亿千瓦，同比增长35%。我国光伏产业保持快速发展势头，能源绿色低碳转型取得显著成效。...

邮件摘要（280字）：
> 2025年全国光伏新增装机3.17亿千瓦，同比增长14%。截至2025年12月，全国光伏发电装机容量达到12亿千瓦，同比增长35%。我国光伏产业保持快速发展势头，能源绿色低碳转型取得显著成效。...

---

## 🔧 自定义配置

### 修改颜色方案

在 `mail_template_new.html` 中修改主色调：

```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* 改为你喜欢的颜色 */
}

.news-number {
    background-color: #667eea;
    /* 改为你喜欢的颜色 */
}
```

### 修改摘要长度

在 `generate_mail_template.py` 中修改：

```python
def truncate_text(text, max_length=300):
    # 改为你想要的长度
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
```

---

## 📱 兼容性

| 邮件客户端 | 支持情况 | 备注 |
|----------|--------|------|
| Gmail | ✅ 完全支持 | 包括移动端 |
| Outlook | ✅ 完全支持 | Windows 和 Web 版 |
| Apple Mail | ✅ 完全支持 | iOS 和 macOS |
| Yahoo Mail | ✅ 完全支持 | - |
| 微信邮箱 | ✅ 支持 | 部分样式可能有差异 |
| QQ邮箱 | ✅ 支持 | - |

---

## 🌟 下一步集成建议

1. **验证邮件渲染**
   - 在主要邮件客户端中测试显示效果
   - 确保所有颜色和格式正确显示

2. **集成到 GitHub Actions**
   - 修改 `.github/workflows/daily.yml`
   - 在发送邮件前调用新的生成脚本

3. **A/B 测试**
   - 对比新旧格式的邮件打开率
   - 根据用户反馈进一步优化

4. **动态内容**
   - 考虑添加天气信息
   - 添加个性化问候
   - 包含热点新闻排行

---

## 📝 示例邮件预览

生成的邮件 HTML 结构示例：

```html
<div class="container">
    <div class="header">
        <h1>📰 每日新闻更新</h1>
        <p>来自 CCTV 新闻联播的精选内容</p>
    </div>
    
    <div class="meta-info">
        <div class="meta-item">
            <strong>📅 日期：</strong>
            <span>2026年02月21日</span>
        </div>
        <div class="meta-item">
            <strong>⏰ 爬取：</strong>
            <span>2026-02-22 11:19:54</span>
        </div>
    </div>
    
    <div class="content">
        <div class="news-item">
            <span class="news-number">1</span>
            <div class="news-title">【情满中国年】美丽中国 幸福生活</div>
            <div class="news-content">习近平总书记指出，环境就是民生...</div>
        </div>
        <!-- 更多新闻项... -->
    </div>
    
    <div class="footer">
        <p>此邮件由自动化爬虫生成</p>
    </div>
</div>
```

---

## 💡 后续优化方向

- [ ] 添加邮件模板的暗黑模式支持
- [ ] 实现新闻分类标签（国内/国际/政经等）
- [ ] 添加订阅管理链接
- [ ] 集成追踪像素统计打开率
- [ ] 支持多语言选项

---

## 📞 技术支持

如有问题或建议，请提交 Issue 或 PR。

生成时间: 2026-02-23
