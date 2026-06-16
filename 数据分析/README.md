# 习题册数据分析

## 文件结构

```
数据分析/
├── README.md                          # 本文件
├── 408分析报告.md                      # 408 四科完成情况（含图表）
├── 软微分析报告.md                     # 软微历年成绩分析
│
├── scripts/
│   ├── export_xlsx_to_csv.py          # xlsx → CSV 导出（含公式求值器）
│   ├── analyze_csv_folder.py          # 批量分析 CSV → 报告+图表
│   ├── visualize_408.py               # 408 四科可视化（6张图+报告）
│   └── rw_analyze.py                  # 软微初试/录取成绩分析
│
├── csv/                               # 导出的 CSV 文件
│   ├── manifest.csv
│   ├── 01_张宇1000题.csv
│   ├── 02_王道操作系统.csv
│   ├── 03_王道计组.csv
│   ├── 04_王道数据结构.csv
│   └── 05_王道计网.csv
│
├── 软微/                              # 软微原始数据 (2020-2026)
│   ├── 20xx初试.xlsx
│   └── 20xx录取.xlsx
│
├── 分析结果/                           # 逐表分析输出
│   ├── 01_张宇1000题/
│   ├── 02_王道操作系统/
│   ├── 03_王道计组/
│   ├── 04_王道数据结构/
│   ├── 05_王道计网/
│   └── _汇总/                         # 横向对比
│
├── figures/                           # 图表输出
│   ├── 408_overview.png               # 四科总览
│   ├── 408_heatmap.png                # 章节热力图
│   ├── 408_chapter_ranking.png        # 章节排名
│   ├── 408_weak_sections.png          # 薄弱小节
│   ├── 408_zhenti_vs_zibian.png       # 真题 vs 自编
│   ├── 408_distribution.png           # 分布 & 散点
│   └── 软微/                          # 软微图表 (27张)
│
└── 习题册数据分析.ipynb               # Jupyter Notebook
```

## 当前 408 进度

| 科目 | 正确率 | 题量 | 状态 |
|:---|:---:|:---:|:---|
| DS 数据结构 | 85.4% | 595 | 一刷完成 |
| CO 计组 | 73.8% | 592 | 一刷完成 |
| OS 操作系统 | 74.5% | 650 | 一刷完成 |
| CN 计网 | — | — | 未开始 |
| **三科合计** | **77.8%** | **1837** | 估分 ~119 |

## 运行指令

### 导出 CSV
```powershell
& 'D:\Miniconda3\envs\py313_pip_only\python.exe' 数据分析\scripts\export_xlsx_to_csv.py
```

### 批量分析
```powershell
& 'D:\Miniconda3\envs\py313_pip_only\python.exe' 数据分析\scripts\analyze_csv_folder.py --clean
```

### 408 可视化
```powershell
& 'D:\Miniconda3\envs\py313_pip_only\python.exe' 数据分析\scripts\visualize_408.py
```

### 软微分析
```powershell
& 'D:\Miniconda3\envs\py313_pip_only\python.exe' 数据分析\scripts\rw_analyze.py
```

## 中文字体

所有脚本使用统一的字体配置（`msyh.ttc` > `simhei.ttf` > `simsun.ttc`），`sns.set_style` 之后需重新设置 `font.sans-serif` 和 `font.family`。
