# 考研资料采集器

一个面向 Obsidian 的小型网页采集项目，适合把知乎专栏、B 站专栏中的公开考研资料整理成 Markdown 笔记。

## 功能

- 支持抓取 B 站专栏公开文章
- 支持抓取知乎专栏
  - 优先使用浏览器 Cookie 请求公开文章页
  - 如果知乎拦截请求，可改用本地保存的 HTML 导入
- 输出 Obsidian 友好的 Markdown
- 自动写入来源、抓取时间、标签、原文链接
- 支持批量导入链接列表

## 目录结构

```text
.scripts/kaoyan_clipper/
├── clipper.py              # 主程序
├── requirements.txt        # 依赖
├── urls_example.txt        # 链接列表示例
└── README.md               # 使用说明
```

默认输出目录：

```text
资料收集/
└── 网页剪藏/
```

## 安装

在仓库根目录执行：

```powershell
pip install -r .scripts/kaoyan_clipper/requirements.txt
```

## 快速开始

### 1. 抓取单篇 B 站专栏

```powershell
python .scripts/kaoyan_clipper/clipper.py clip https://www.bilibili.com/read/cv19693873
```

### 2. 批量抓取链接

```powershell
python .scripts/kaoyan_clipper/clipper.py batch .scripts/kaoyan_clipper/urls_example.txt
```

### 3. 自定义输出目录

```powershell
python .scripts/kaoyan_clipper/clipper.py batch .scripts/kaoyan_clipper/urls_example.txt --output "资料收集/考研经验"
```

## 知乎支持

知乎对未登录请求比较严格，建议二选一：

### 方案 A：使用浏览器 Cookie

把浏览器里 `zhihu.com` 的 Cookie 复制到环境变量：

```powershell
$env:ZHIHU_COOKIE="你的完整 Cookie"
python .scripts/kaoyan_clipper/clipper.py clip "https://zhuanlan.zhihu.com/p/xxxxxx"
```

### 方案 B：导入本地保存的 HTML

先在浏览器中打开文章，使用“网页另存为”保存 HTML，然后执行：

```powershell
python .scripts/kaoyan_clipper/clipper.py import-html "C:\path\to\zhihu_article.html" --source zhihu
```

## 输入文件格式

批量文件中每行一个链接，支持注释：

```text
# 考研经验
https://www.bilibili.com/read/cv19693873
https://zhuanlan.zhihu.com/p/123456789
```

## 注意事项

- 仅建议用于采集公开内容，方便个人学习整理
- 不包含验证码绕过、登录破解、反爬绕过等能力
- 知乎页面结构变化较快，若直抓失效，可改用本地 HTML 导入
- 图片默认以原链接形式写入 Markdown，不会自动下载到本地

## 适合你的使用方式

你可以把常看的“考研经验 / 复习规划 / 408 技巧 / 数学做题方法”链接存到一个文本文件里，定期批量执行，自动沉淀进 Obsidian。

例如你可以专门建一个：

```text
.scripts/kaoyan_clipper/urls_kaoyan.txt
```

里面分类收集：

```text
# 数学复习方法
https://www.bilibili.com/read/cvxxxxxx

# 408 经验帖
https://www.bilibili.com/read/cvyyyyyy

# 知乎经验帖
https://zhuanlan.zhihu.com/p/zzzzzz
```

然后每周执行一次：

```powershell
python .scripts/kaoyan_clipper/clipper.py batch .scripts/kaoyan_clipper/urls_kaoyan.txt --output "资料收集/考研经验汇总"
```
