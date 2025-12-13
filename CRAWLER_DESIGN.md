# 新爬虫逻辑设计文档

## 问题分析

当前问题：
- 原逻辑直接访问 `http://mrxwlb.com/YYYY/MM/DD/YYYY年MM月DD日新闻联播文字版/`
- 但实际网站结构是：`http://mrxwlb.com/YYYY/MM/DD/` 是一个目录页面
- 目录页面可能包含多个新闻文章，且这些文章的日期可能不是目录日期（可能是补发的）

## 新设计思路

### 1. 目录页面访问
- 访问 `http://mrxwlb.com/YYYY/MM/DD/` 或 `http://mrxwlb.com/YYYY/M/D/`（两种格式）
- 解析HTML，提取所有新闻文章链接

### 2. 新闻链接提取
- 从目录页面中找到所有指向新闻文章的链接
- 链接特征：
  - 包含日期格式（如 `2022年12月12日新闻联播文字版`）
  - 或包含 `/YYYY/MM/DD/` 路径模式

### 3. 实际日期提取
- 访问每个新闻链接
- 从页面标题（`<h1>` 或 `<title>`）中提取实际日期
- 使用 `extract_date_from_title()` 函数

### 4. 内容爬取与保存
- 爬取每个新闻页面的完整内容
- 使用实际日期保存文件：`data/news/YYYYMMDD.md`
- 如果同一日期有多个新闻，需要处理重复情况（追加或覆盖）

## 函数设计

### 核心函数

#### 1. `build_directory_url(date: datetime, use_zero_padding: bool = True) -> str`
构建目录页面URL
- 输入：日期对象
- 输出：目录URL（如 `http://mrxwlb.com/2022/12/12/`）

#### 2. `fetch_news_links_from_directory(date: datetime) -> List[str]`
从目录页面提取所有新闻链接
- 输入：日期对象
- 输出：新闻链接列表
- 逻辑：
  1. 尝试两种URL格式（两位数/个位数）
  2. 解析HTML，查找所有新闻链接
  3. 过滤出有效的新闻链接（包含日期信息）

#### 3. `crawl_news_from_directory(date: datetime) -> List[Tuple[str, str, datetime]]`
从目录页面爬取所有新闻
- 输入：日期对象（目录日期）
- 输出：新闻列表 `[(标题, 内容, 实际日期), ...]`
- 逻辑：
  1. 获取目录页面的所有新闻链接
  2. 遍历每个链接
  3. 访问新闻页面，提取标题和内容
  4. 从标题中提取实际日期
  5. 返回所有新闻

#### 4. `crawl_and_save_from_directory(date: datetime) -> Dict[str, int]`
从目录页面爬取并保存所有新闻
- 输入：日期对象（目录日期）
- 输出：统计信息 `{"success": 成功数, "failed": 失败数, "skipped": 跳过数}`
- 逻辑：
  1. 调用 `crawl_news_from_directory()` 获取所有新闻
  2. 对每个新闻，检查文件是否已存在
  3. 如果不存在或需要更新，保存文件
  4. 返回统计信息

### 辅助函数

#### `extract_news_links_from_html(html: str) -> List[str]`
从HTML中提取新闻链接
- 使用BeautifulSoup解析
- 查找所有 `<a>` 标签
- 过滤出包含日期格式或符合新闻URL模式的链接

## 工作流程

```
用户指定日期 (2022-12-12)
    ↓
构建目录URL (http://mrxwlb.com/2022/12/12/)
    ↓
访问目录页面，提取所有新闻链接
    ↓
遍历每个新闻链接
    ↓
访问新闻页面 → 提取标题和内容 → 从标题提取实际日期
    ↓
按实际日期保存文件 (data/news/20221212.md)
```

## 处理边界情况

1. **目录页面404**：记录为缺失日期
2. **目录页面为空**：记录为缺失日期
3. **新闻链接无效**：跳过，继续处理下一个
4. **无法提取日期**：使用目录日期作为备选
5. **同一日期多个新闻**：
   - 方案A：覆盖（只保留最新的）
   - 方案B：追加（合并内容）
   - 方案C：重命名（添加序号）
   - **推荐：方案A（覆盖）**，因为通常同一日期只有一个新闻

## 兼容性考虑

- 保留原有的 `fetch_news_by_date()` 函数，用于直接访问已知URL
- 新增 `fetch_news_from_directory()` 函数，用于目录页面爬取
- `crawl_and_save()` 函数可以选择使用哪种方式

## 示例代码结构

```python
def build_directory_url(date: datetime, use_zero_padding: bool = True) -> str:
    """构建目录页面URL"""
    pass

def fetch_news_links_from_directory(date: datetime) -> List[str]:
    """从目录页面提取所有新闻链接"""
    pass

def crawl_news_from_directory(date: datetime) -> List[Tuple[str, str, datetime]]:
    """从目录页面爬取所有新闻"""
    pass

def crawl_and_save_from_directory(date: datetime) -> Dict[str, int]:
    """从目录页面爬取并保存所有新闻"""
    pass
```

## 测试计划

1. 测试目录页面访问（正常情况）
2. 测试目录页面404（缺失情况）
3. 测试目录页面包含多个新闻（补发情况）
4. 测试新闻链接提取准确性
5. 测试日期提取准确性
6. 测试文件保存逻辑（重复日期处理）

