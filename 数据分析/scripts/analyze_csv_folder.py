from __future__ import annotations

import argparse
import re
import shutil
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[2]
PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CSV_DIR = PROJECT_DIR / "csv"
DEFAULT_OUT_DIR = PROJECT_DIR / "分析结果"


def safe_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(name)).strip()
    return cleaned or "未命名表格"


def setup_plot_style() -> str:
    warnings.filterwarnings("ignore")
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    preferred_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Arial Unicode MS",
    ]
    chosen_font = next((font for font in preferred_fonts if font in available_fonts), "DejaVu Sans")
    plt.rcParams["font.sans-serif"] = [chosen_font]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 130
    sns.set_theme(style="whitegrid", font=chosen_font, rc={"axes.unicode_minus": False})
    return chosen_font


def to_number(value) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip().replace(",", "").replace("，", "")
    if text == "":
        return np.nan
    if text.endswith(("%", "％")):
        number = pd.to_numeric(text[:-1].strip(), errors="coerce")
        return number / 100 if pd.notna(number) else np.nan
    return pd.to_numeric(text, errors="coerce")


def rate(correct: float, total: float, fallback=np.nan) -> float:
    if pd.notna(total) and total > 0:
        return correct / total
    return fallback if pd.notna(fallback) else np.nan


def read_raw_csv(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, header=None, dtype=str, encoding="utf-8-sig").fillna("")
    return raw.reindex(columns=range(max(9, raw.shape[1])), fill_value="")


def parse_exercise_csv(path: Path) -> tuple[pd.DataFrame, dict]:
    raw = read_raw_csv(path)
    title_candidates = raw.iloc[:, 0].astype(str).str.strip()
    title = title_candidates[title_candidates.ne("")].iloc[0] if title_candidates.ne("").any() else path.stem

    header_mask = raw.iloc[:, 0].astype(str).str.strip().isin(["小节", "章节"])
    header_idx = int(header_mask[header_mask].index[0]) if header_mask.any() else 3

    records: list[dict] = []
    current_chapter = "未分章"
    current_chapter_no = np.nan

    for _, row in raw.iloc[header_idx + 1 :].iterrows():
        label = str(row[0]).strip()
        if not label:
            continue

        chapter_match = re.match(r"^第(\d+)章", label)
        if chapter_match:
            current_chapter = label
            current_chapter_no = int(chapter_match.group(1))
            continue

        if label.replace(" ", "") in {"合计", "总计"} or label.startswith("【"):
            continue

        first_total_raw = to_number(row[2])
        first_correct_raw = to_number(row[3])
        first_rate_raw = to_number(row[4])
        second_total_raw = to_number(row[6])
        second_correct_raw = to_number(row[7])
        second_rate_raw = to_number(row[8])

        first_total = 0 if pd.isna(first_total_raw) else int(first_total_raw)
        first_correct = 0 if pd.isna(first_correct_raw) else int(first_correct_raw)
        second_total = 0 if pd.isna(second_total_raw) else int(second_total_raw)
        second_correct = 0 if pd.isna(second_correct_raw) else int(second_correct_raw)
        first_rate = rate(first_correct, first_total, first_rate_raw)
        second_rate = rate(second_correct, second_total, second_rate_raw)
        has_first_data = first_total > 0 or first_correct > 0 or pd.notna(first_rate_raw)
        has_second_data = second_total > 0 or second_correct > 0 or pd.notna(second_rate_raw)

        section_match = re.match(r"^(\d+(?:\.\d+)+)", label)
        records.append(
            {
                "source_file": path.name,
                "title": title,
                "chapter": current_chapter,
                "chapter_no": current_chapter_no,
                "section": label,
                "section_no": section_match.group(1) if section_match else "",
                "date_or_page": str(row[1]).strip(),
                "first_total": first_total,
                "first_correct": first_correct,
                "first_wrong": max(first_total - first_correct, 0),
                "first_rate": first_rate,
                "second_total": second_total,
                "second_correct": second_correct,
                "second_wrong": max(second_total - second_correct, 0),
                "second_rate": second_rate,
                "has_first_data": has_first_data,
                "has_second_data": has_second_data,
            }
        )

    df = pd.DataFrame(records)
    if not df.empty:
        df["chapter_no"] = pd.to_numeric(df["chapter_no"], errors="coerce")
        df["section_order"] = df.groupby("chapter").cumcount() + 1
        df["first_rate_pct"] = df["first_rate"] * 100
        df["second_rate_pct"] = df["second_rate"] * 100

    meta = {
        "source_file": path.name,
        "title": title,
        "header_idx": header_idx,
        "source_path": str(path),
    }
    return df, meta


def make_overall_summary(df: pd.DataFrame, meta: dict) -> pd.DataFrame:
    valid_first = df[df["first_total"] > 0] if not df.empty else df
    valid_second = df[df["second_total"] > 0] if not df.empty else df
    first_total = valid_first["first_total"].sum() if not valid_first.empty else 0
    first_correct = valid_first["first_correct"].sum() if not valid_first.empty else 0
    second_total = valid_second["second_total"].sum() if not valid_second.empty else 0
    second_correct = valid_second["second_correct"].sum() if not valid_second.empty else 0
    return pd.DataFrame(
        [
            {
                "source_file": meta["source_file"],
                "title": meta["title"],
                "sections_total": len(df),
                "sections_with_first_data": len(valid_first),
                "first_total": first_total,
                "first_correct": first_correct,
                "first_wrong": first_total - first_correct,
                "first_rate": first_correct / first_total if first_total else np.nan,
                "first_avg_section_rate": valid_first["first_rate"].mean() if not valid_first.empty else np.nan,
                "sections_with_second_data": len(valid_second),
                "second_total": second_total,
                "second_correct": second_correct,
                "second_wrong": second_total - second_correct,
                "second_rate": second_correct / second_total if second_total else np.nan,
            }
        ]
    )


def make_chapter_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    grouped = (
        df.groupby(["chapter_no", "chapter"], dropna=False)
        .agg(
            sections_total=("section", "count"),
            sections_with_first_data=("first_total", lambda s: int((s > 0).sum())),
            first_total=("first_total", "sum"),
            first_correct=("first_correct", "sum"),
            first_wrong=("first_wrong", "sum"),
            avg_section_rate=("first_rate", "mean"),
            sections_with_second_data=("second_total", lambda s: int((s > 0).sum())),
            second_total=("second_total", "sum"),
            second_correct=("second_correct", "sum"),
            second_wrong=("second_wrong", "sum"),
        )
        .reset_index()
    )
    grouped["first_rate"] = grouped["first_correct"] / grouped["first_total"].replace(0, np.nan)
    grouped["second_rate"] = grouped["second_correct"] / grouped["second_total"].replace(0, np.nan)

    valid = df[df["first_total"] > 0]
    if not valid.empty:
        weak = (
            valid.sort_values(["chapter_no", "first_rate", "first_total"], ascending=[True, True, False])
            .groupby("chapter", as_index=False)
            .first()[["chapter", "section", "first_rate"]]
            .rename(columns={"section": "weakest_section", "first_rate": "weakest_rate"})
        )
        grouped = grouped.merge(weak, on="chapter", how="left")
    else:
        grouped["weakest_section"] = ""
        grouped["weakest_rate"] = np.nan

    return grouped.sort_values("chapter_no")


def save_no_data_figure(path: Path, title: str, message: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    ax.text(0.5, 0.62, title, ha="center", va="center", fontsize=18, fontweight="bold")
    ax.text(0.5, 0.38, message, ha="center", va="center", fontsize=13, color="#666")
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_section_heatmap(df: pd.DataFrame, meta: dict, out_path: Path) -> None:
    valid = df[df["first_total"] > 0].copy()
    if valid.empty:
        save_no_data_figure(out_path, meta["title"], "暂无已填写题量的小节，无法生成正确率热力图")
        return

    heat_matrix = valid.pivot_table(index="chapter", columns="section_order", values="first_rate", aggfunc="mean")
    annot_matrix = (
        valid.pivot_table(index="chapter", columns="section_order", values="section_no", aggfunc="first")
        .reindex_like(heat_matrix)
        .fillna("")
    )
    annot = heat_matrix.copy().astype(object)
    for row in heat_matrix.index:
        for col in heat_matrix.columns:
            value = heat_matrix.loc[row, col]
            label = annot_matrix.loc[row, col]
            annot.loc[row, col] = "" if pd.isna(value) else f"{label}\n{value:.0%}"

    fig_w = max(14, 1.55 * heat_matrix.shape[1] + 5)
    fig_h = max(7, 1.15 * heat_matrix.shape[0] + 2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    sns.heatmap(
        heat_matrix,
        annot=annot,
        fmt="",
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        linewidths=1.0,
        linecolor="white",
        cbar_kws={"label": "一刷正确率"},
        annot_kws={"fontsize": 11, "fontweight": "bold"},
        ax=ax,
    )
    ax.set_title(f"{meta['title']}：小节正确率热力图", fontsize=18, fontweight="bold", pad=18)
    ax.set_xlabel("本章内小节序号", fontsize=13)
    ax.set_ylabel("章节", fontsize=13)
    ax.tick_params(axis="x", labelrotation=0, labelsize=11)
    ax.tick_params(axis="y", labelrotation=0, labelsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def annotate_rate_axis(ax, values, x_offset=0.012) -> None:
    for patch, value in zip(ax.patches, values):
        if pd.isna(value):
            continue
        width = patch.get_width()
        y = patch.get_y() + patch.get_height() / 2
        ax.text(min(width + x_offset, 0.985), y, f"{value:.1%}", va="center", ha="left", fontsize=10, color="#333")


def save_chapter_analysis(df: pd.DataFrame, chapter_df: pd.DataFrame, meta: dict, out_path: Path) -> None:
    valid = df[df["first_total"] > 0].copy()
    if valid.empty or chapter_df.empty or chapter_df["first_total"].sum() == 0:
        save_no_data_figure(out_path, meta["title"], "暂无已填写题量的小节，无法生成章节分析图")
        return

    fig, axes = plt.subplots(2, 2, figsize=(18, 13))
    plot_chapter = chapter_df[chapter_df["first_total"] > 0].copy()
    sns.barplot(data=plot_chapter, y="chapter", x="first_rate", hue="chapter", palette="RdYlGn", legend=False, ax=axes[0, 0])
    axes[0, 0].set_title("各章节一刷正确率", fontsize=15, fontweight="bold")
    axes[0, 0].set_xlim(0, 1)
    axes[0, 0].xaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    annotate_rate_axis(axes[0, 0], plot_chapter["first_rate"].tolist())

    chapter_long = plot_chapter.melt(
        id_vars="chapter",
        value_vars=["first_total", "first_correct", "first_wrong"],
        var_name="metric",
        value_name="count",
    )
    chapter_long["metric"] = chapter_long["metric"].map({"first_total": "总题", "first_correct": "正确", "first_wrong": "错误"})
    sns.barplot(data=chapter_long, y="chapter", x="count", hue="metric", ax=axes[0, 1])
    axes[0, 1].set_title("各章节题量/正确/错误", fontsize=15, fontweight="bold")
    axes[0, 1].legend(title="")

    sns.histplot(data=valid, x="first_rate", bins=10, kde=True, color="#5B9BD5", ax=axes[1, 0])
    axes[1, 0].set_title("小节正确率分布", fontsize=15, fontweight="bold")
    axes[1, 0].set_xlim(0, 1)
    axes[1, 0].xaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")

    sns.scatterplot(data=valid, x="first_total", y="first_rate", size="first_total", hue="chapter", sizes=(60, 420), alpha=0.82, ax=axes[1, 1])
    axes[1, 1].set_title("小节题量 vs 正确率", fontsize=15, fontweight="bold")
    axes[1, 1].yaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    axes[1, 1].set_ylim(0, 1.05)
    for _, row in valid.nsmallest(5, "first_rate").iterrows():
        axes[1, 1].annotate(row["section_no"], (row["first_total"], row["first_rate"]), xytext=(5, 5), textcoords="offset points", fontsize=10)
    axes[1, 1].legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)

    for ax in axes.flat:
        ax.set_xlabel(ax.get_xlabel(), fontsize=12)
        ax.set_ylabel(ax.get_ylabel(), fontsize=12)
        ax.tick_params(labelsize=10)

    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_cross_table_analysis(summary_df: pd.DataFrame, out_path: Path) -> None:
    if summary_df.empty:
        save_no_data_figure(out_path, "全部 CSV 横向对比", "没有可分析的 CSV")
        return

    plot_df = summary_df.copy()
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    sns.barplot(data=plot_df, y="source_file", x="first_rate", hue="source_file", palette="RdYlGn", legend=False, ax=axes[0])
    axes[0].set_title("各 CSV 一刷正确率对比", fontsize=15, fontweight="bold")
    axes[0].set_xlim(0, 1)
    axes[0].xaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    annotate_rate_axis(axes[0], plot_df["first_rate"].tolist())

    heat_metrics = plot_df.set_index("source_file")[["sections_with_first_data", "first_total", "first_wrong", "first_rate", "first_avg_section_rate"]]
    heat_norm = heat_metrics.copy()
    for col in ["sections_with_first_data", "first_total", "first_wrong"]:
        max_val = heat_norm[col].max()
        heat_norm[col] = heat_norm[col] / max_val if max_val else 0
    sns.heatmap(
        heat_norm,
        annot=heat_metrics.round(3),
        fmt="",
        cmap="YlGnBu",
        linewidths=1,
        linecolor="white",
        ax=axes[1],
        annot_kws={"fontsize": 10},
    )
    axes[1].set_title("各 CSV 指标热力图（题量列归一化着色）", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_report(out_dir: Path, meta: dict, overall: pd.DataFrame, chapter_df: pd.DataFrame, weak_df: pd.DataFrame) -> None:
    item = overall.iloc[0].to_dict() if not overall.empty else {}

    def fmt_rate(value) -> str:
        return "" if pd.isna(value) else f"{value:.2%}"

    lines = [
        f"# {meta['title']}",
        "",
        f"- 来源文件：`{meta['source_file']}`",
        f"- 小节总数：{int(item.get('sections_total', 0) or 0)}",
        f"- 已填写一刷小节：{int(item.get('sections_with_first_data', 0) or 0)}",
        f"- 一刷总题：{int(item.get('first_total', 0) or 0)}",
        f"- 一刷正确：{int(item.get('first_correct', 0) or 0)}",
        f"- 一刷正确率：{fmt_rate(item.get('first_rate', np.nan))}",
        "",
        "## 文件",
        "",
        f"- `{meta['source_file']}`：原始 CSV 副本",
        "- `cleaned_records.csv`：清洗后小节明细",
        "- `overall_summary.csv`：总体指标",
        "- `chapter_summary.csv`：章节汇总",
        "- `weak_sections_top10.csv`：薄弱小节",
        "- `section_heatmap.png`：小节正确率热力图",
        "- `chapter_analysis.png`：章节与分布分析",
    ]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def analyze_one_csv(path: Path, out_root: Path, clean_existing: bool = False) -> dict:
    folder = out_root / safe_filename(path.stem)
    if clean_existing and folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)

    df, meta = parse_exercise_csv(path)
    overall = make_overall_summary(df, meta)
    chapter_df = make_chapter_summary(df)
    weak_df = (
        df[df["first_total"] > 0]
        .sort_values(["first_rate", "first_total"], ascending=[True, False])
        .head(10)
        if not df.empty
        else pd.DataFrame()
    )

    source_copy = folder / path.name
    if source_copy.resolve() != path.resolve():
        shutil.copy2(path, source_copy)
    df.to_csv(folder / "cleaned_records.csv", index=False, encoding="utf-8-sig")
    overall.to_csv(folder / "overall_summary.csv", index=False, encoding="utf-8-sig")
    chapter_df.to_csv(folder / "chapter_summary.csv", index=False, encoding="utf-8-sig")
    weak_df.to_csv(folder / "weak_sections_top10.csv", index=False, encoding="utf-8-sig")

    save_section_heatmap(df, meta, folder / "section_heatmap.png")
    save_chapter_analysis(df, chapter_df, meta, folder / "chapter_analysis.png")
    write_report(folder, meta, overall, chapter_df, weak_df)
    return {
        "folder": str(folder),
        **overall.iloc[0].to_dict(),
    }


def scan_csv_files(csv_dir: Path) -> list[Path]:
    return sorted(path for path in csv_dir.glob("*.csv") if path.name.lower() != "manifest.csv")


def analyze_csv_folder(csv_dir: Path = DEFAULT_CSV_DIR, out_dir: Path = DEFAULT_OUT_DIR, clean_existing: bool = False) -> pd.DataFrame:
    setup_plot_style()
    csv_dir = Path(csv_dir)
    out_dir = Path(out_dir)
    if clean_existing and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    all_records = []
    for path in scan_csv_files(csv_dir):
        result = analyze_one_csv(path, out_dir, clean_existing=False)
        rows.append(result)
        table_records = pd.read_csv(Path(result["folder"]) / "cleaned_records.csv", encoding="utf-8-sig")
        all_records.append(table_records)
        print(f"已分析：{path.name} -> {result['folder']}")

    summary = pd.DataFrame(rows)
    summary_dir = out_dir / "_汇总"
    summary_dir.mkdir(exist_ok=True)
    summary.to_csv(summary_dir / "all_tables_summary.csv", index=False, encoding="utf-8-sig")
    if all_records:
        pd.concat(all_records, ignore_index=True).to_csv(summary_dir / "all_cleaned_records.csv", index=False, encoding="utf-8-sig")
    save_cross_table_analysis(summary, summary_dir / "all_tables_comparison.png")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan csv folder, analyze every exercise CSV, and export results to per-table folders.")
    parser.add_argument("--csv-dir", type=Path, default=DEFAULT_CSV_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--clean", action="store_true", help="Delete existing output folder before exporting.")
    args = parser.parse_args()

    summary = analyze_csv_folder(args.csv_dir.resolve(), args.out_dir.resolve(), clean_existing=args.clean)
    print(f"\n完成：{len(summary)} 个 CSV")
    print(f"输出目录：{args.out_dir.resolve()}")


if __name__ == "__main__":
    main()
