# 习题册数据分析

这个项目先把 `习题册excel.xlsx` 拆成 CSV，方便后续用 Python 做分析。

## 文件结构

- `scripts/export_xlsx_to_csv.py`：把 xlsx 的每个可见工作表导出为单独 CSV。
- `scripts/analyze_csv_folder.py`：扫描 `csv/` 下所有 CSV，逐表分析并导出到对应文件夹。
- `csv/`：导出的 CSV 文件。
- `csv/manifest.csv`：记录每个工作表对应的 CSV 文件。
- `分析结果/`：批量分析输出目录，每张表一个文件夹，另有 `_汇总/` 横向对比。
- `习题册数据分析.ipynb`：Notebook 版本，包含单表测试和批量导出入口。

## 重新导出

在 Obsidian Vault 根目录运行：

```powershell
& 'D:\Miniconda3\envs\py313_pip_only\python.exe' 数据分析\scripts\export_xlsx_to_csv.py
```

说明：CSV 本身不能保存多工作表结构，所以这里采用“一张工作表一个 CSV”的方式。隐藏工作表默认不会导出。

## 批量分析并导出

在 Obsidian Vault 根目录运行：

```powershell
& 'D:\Miniconda3\envs\py313_pip_only\python.exe' 数据分析\scripts\analyze_csv_folder.py --clean
```

输出会进入 `数据分析/分析结果/`：

- `01_张宇1000题/`、`02_王道操作系统/` 等：每张 CSV 对应一个文件夹，便于留存。
- 每个表格文件夹包含原始 CSV 副本、`cleaned_records.csv`、`overall_summary.csv`、`chapter_summary.csv`、`weak_sections_top10.csv`、`section_heatmap.png`、`chapter_analysis.png` 和 `report.md`。
- `_汇总/` 包含 `all_tables_summary.csv`、`all_cleaned_records.csv` 和 `all_tables_comparison.png`。

如果不想清空旧的分析输出，可以去掉 `--clean`。
