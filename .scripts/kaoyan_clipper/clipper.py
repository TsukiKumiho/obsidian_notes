import argparse
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_OUTPUT_DIR = Path("资料收集") / "网页剪藏"
REQUEST_TIMEOUT = 20


@dataclass
class ClipResult:
    source: str
    title: str
    author: str = ""
    url: str = ""
    published_at: str = ""
    tags: List[str] = field(default_factory=list)
    summary: str = ""
    content_markdown: str = ""


class ClipperError(Exception):
    pass


def fetch_text(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    merged_headers = {"User-Agent": USER_AGENT}
    if headers:
        merged_headers.update(headers)

    request = Request(url, headers=merged_headers)
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, "ignore")
    except HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "ignore")
        except Exception:
            detail = str(exc)
        raise ClipperError(f"请求失败: HTTP {exc.code} {detail[:180]}") from exc
    except URLError as exc:
        raise ClipperError(f"网络请求失败: {exc}") from exc


def fetch_json(url: str, headers: Optional[Dict[str, str]] = None) -> Dict:
    payload = fetch_text(url, headers=headers)
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ClipperError("接口返回的不是合法 JSON 数据。") from exc


def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\\\|?*]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:120] or "未命名资料"


def iso_now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    bits = [bit for bit in parsed.path.split("/") if bit]
    if bits:
        return bits[-1]
    return parsed.netloc


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_asset_url(url: str) -> str:
    if url.startswith("//"):
        return f"https:{url}"
    return url


def extract_bilibili_state(html: str) -> Dict:
    marker = "window.__INITIAL_STATE__="
    start = html.find(marker)
    if start == -1:
        raise ClipperError("未找到 B 站页面状态数据，页面结构可能已变化。")

    start += len(marker)
    end_marker = ";</script>"
    end = html.find(end_marker, start)
    if end == -1:
        raise ClipperError("未能完整提取 B 站页面状态数据。")

    payload = html[start:end].strip()
    return json.loads(payload)


def render_bilibili_nodes(nodes: List[Dict]) -> str:
    parts: List[str] = []
    for node in nodes:
        node_type = node.get("type")
        if node_type == "TEXT_NODE_TYPE_WORD":
            word = node.get("word", {})
            text = word.get("words", "")
            style = word.get("style", {}) or {}
            if style.get("bold"):
                text = f"**{text}**"
            if style.get("italic"):
                text = f"*{text}*"
            if style.get("strike"):
                text = f"~~{text}~~"
            parts.append(text)
        elif node_type == "TEXT_NODE_TYPE_LINK":
            link = node.get("link", {})
            text = link.get("text", link.get("url", "链接"))
            url = link.get("url", "")
            parts.append(f"[{text}]({url})" if url else text)
        elif node_type == "TEXT_NODE_TYPE_AT":
            at = node.get("at", {})
            parts.append(f"@{at.get('text', '').strip('@')}")
        elif node_type == "TEXT_NODE_TYPE_EMOJI":
            emoji = node.get("emoji", {})
            parts.append(emoji.get("text", ""))
    return normalize_whitespace("".join(parts))


def bilibili_content_to_markdown(modules: List[Dict]) -> str:
    lines: List[str] = []

    for module in modules:
        if module.get("module_type") != "MODULE_TYPE_CONTENT":
            continue

        content = module.get("module_content", {})
        paragraphs = content.get("paragraphs", [])
        for para in paragraphs:
            para_type = para.get("para_type")
            if para_type == 1:
                nodes = para.get("text", {}).get("nodes", [])
                text = render_bilibili_nodes(nodes)
                if not text:
                    continue

                plain = re.sub(r"[*_`~\[\]]", "", text).strip()
                is_heading = False
                if len(plain) <= 30:
                    font_sizes = [
                        node.get("word", {}).get("font_size", 0)
                        for node in nodes
                        if node.get("type") == "TEXT_NODE_TYPE_WORD"
                    ]
                    if font_sizes and max(font_sizes) >= 20:
                        is_heading = True

                lines.append(f"## {plain}" if is_heading else text)
                lines.append("")
            elif para_type == 2:
                pics = para.get("pic", {}).get("pics", [])
                for pic in pics:
                    pic_url = normalize_asset_url(pic.get("url", ""))
                    if pic_url:
                        lines.append(f"![]({pic_url})")
                        lines.append("")

    return normalize_whitespace("\n".join(lines))


def extract_bilibili_article_id(url: str) -> str:
    match = re.search(r"/read/cv(\d+)", url)
    if match:
        return match.group(1)

    parsed = urlparse(url)
    query_id = parse_qs(parsed.query).get("id", [])
    if "read/mobile" in parsed.path and query_id:
        return query_id[0]

    raise ClipperError("未能从 B 站链接中解析文章 ID。")


def extract_bilibili_opus_id(url: str) -> Optional[str]:
    match = re.search(r"/opus/(\d+)", url)
    return match.group(1) if match else None


def clip_bilibili_from_state(url: str, html: Optional[str] = None) -> ClipResult:
    if html is None:
        html = fetch_text(url)

    state = extract_bilibili_state(html)
    detail = state.get("detail", {})
    basic = detail.get("basic", {})
    modules = detail.get("modules", [])

    title = ""
    author = ""
    published_at = ""
    tags: List[str] = ["考研资料", "B站专栏"]

    for module in modules:
        module_type = module.get("module_type")
        if module_type == "MODULE_TYPE_TITLE":
            title = module.get("module_title", {}).get("text", "") or title
        elif module_type == "MODULE_TYPE_AUTHOR":
            author_data = module.get("module_author", {})
            author = author_data.get("name", "") or author
            pub_ts = author_data.get("pub_time")
            if isinstance(pub_ts, int) and pub_ts > 0:
                published_at = datetime.fromtimestamp(pub_ts).strftime("%Y-%m-%d %H:%M:%S")

    if not title:
        title = basic.get("title", "").replace(" - 哔哩哔哩", "").strip()
    if not title:
        raise ClipperError("未能解析 B 站文章标题。")

    content_markdown = bilibili_content_to_markdown(modules)
    if not content_markdown:
        raise ClipperError("未能解析 B 站文章正文。")

    return ClipResult(
        source="bilibili",
        title=title,
        author=author,
        url=url,
        published_at=published_at,
        tags=tags,
        content_markdown=content_markdown,
    )


def fetch_bilibili_article_data(article_id: str) -> Dict:
    url = f"https://api.bilibili.com/x/article/view?id={article_id}"
    headers = {
        "Referer": f"https://www.bilibili.com/read/cv{article_id}",
        "Origin": "https://www.bilibili.com",
    }

    last_message = ""
    for attempt in range(3):
        payload = fetch_json(url, headers=headers)
        code = payload.get("code")
        if code == 0 and payload.get("data"):
            return payload["data"]

        last_message = payload.get("message") or payload.get("msg") or f"code={code}"
        if code == -509 and attempt < 2:
            time.sleep(attempt + 1)
            continue
        break

    raise ClipperError(
        f"B站接口暂时不可用：{last_message}。可以稍后重试，或在浏览器打开后改用 import-html 导入。"
    )


def clip_bilibili_from_api(url: str) -> ClipResult:
    article_id = extract_bilibili_article_id(url)
    data = fetch_bilibili_article_data(article_id)

    title = data.get("title", "").strip()
    if not title:
        raise ClipperError("未能解析 B 站文章标题。")

    author = data.get("author", {}).get("name", "").strip()
    summary = normalize_whitespace(data.get("summary", ""))
    published_at = ""
    publish_time = data.get("publish_time") or data.get("ctime")
    if isinstance(publish_time, int) and publish_time > 0:
        published_at = datetime.fromtimestamp(publish_time).strftime("%Y-%m-%d %H:%M:%S")

    content_html = data.get("content", "")
    if not content_html:
        raise ClipperError("B站接口返回了空正文。")

    soup = BeautifulSoup(content_html, "html.parser")
    content_markdown = html_to_markdown_from_soup(soup)
    if not content_markdown:
        raise ClipperError("B站正文转换 Markdown 失败。")

    tags = ["考研资料", "B站专栏"]
    if data.get("type") == 2:
        tags.append("B站笔记")

    return ClipResult(
        source="bilibili",
        title=title,
        author=author,
        url=url,
        published_at=published_at,
        tags=tags,
        summary=summary,
        content_markdown=content_markdown,
    )


def clip_bilibili(url: str) -> ClipResult:
    if extract_bilibili_opus_id(url):
        return clip_bilibili_from_state(url)

    api_error: Optional[Exception] = None
    try:
        return clip_bilibili_from_api(url)
    except Exception as exc:
        api_error = exc

    try:
        return clip_bilibili_from_state(url)
    except Exception as page_exc:
        raise ClipperError(f"{api_error} 页面兜底也失败：{page_exc}") from page_exc


def extract_zhihu_state(html: str) -> Dict:
    match = re.search(r'<script id="js-initialData" type="text/json">(.*?)</script>', html, re.S)
    if not match:
        raise ClipperError("未找到知乎页面初始数据。你可以改用 Cookie 或本地 HTML 导入。")

    raw_json = unescape(match.group(1))
    return json.loads(raw_json)


def html_to_markdown_from_soup(container) -> str:
    parts: List[str] = []

    def visit(node) -> str:
        if getattr(node, "name", None) is None:
            return str(node)

        name = node.name.lower()
        if name in {"h1", "h2", "h3", "h4"}:
            level = min(int(name[1]), 3)
            text = normalize_whitespace(node.get_text("\n", strip=True))
            return f"{'#' * level} {text}\n\n" if text else ""
        if name == "p":
            text = "".join(visit(child) for child in node.children).strip()
            return f"{text}\n\n" if text else ""
        if name in {"strong", "b"}:
            text = "".join(visit(child) for child in node.children).strip()
            return f"**{text}**" if text else ""
        if name in {"em", "i"}:
            text = "".join(visit(child) for child in node.children).strip()
            return f"*{text}*" if text else ""
        if name == "a":
            text = normalize_whitespace(node.get_text(" ", strip=True))
            href = normalize_asset_url(node.get("href", "").strip())
            if href and text:
                return f"[{text}]({href})"
            return text
        if name == "img":
            src = normalize_asset_url(node.get("src") or node.get("data-original") or "")
            return f"![]({src})\n\n" if src else ""
        if name in {"ul", "ol"}:
            lines: List[str] = []
            for li in node.find_all("li", recursive=False):
                text = normalize_whitespace(li.get_text(" ", strip=True))
                if text:
                    lines.append(f"- {text}")
            return "\n".join(lines) + "\n\n" if lines else ""
        if name == "blockquote":
            text = normalize_whitespace(node.get_text("\n", strip=True))
            if not text:
                return ""
            quoted = "\n".join(f"> {line}" for line in text.splitlines())
            return f"{quoted}\n\n"
        if name == "br":
            return "\n"

        return "".join(visit(child) for child in node.children)

    for child in container.children:
        rendered = visit(child)
        if rendered:
            parts.append(rendered)

    return normalize_whitespace("".join(parts))


def extract_zhihu_article_from_state(state: Dict, url: str) -> ClipResult:
    initial_state = state.get("initialState", {})
    entities = initial_state.get("entities", {})
    articles = entities.get("articles", {})
    if not articles:
        raise ClipperError("知乎页面里没有找到文章实体数据。")

    article = next(iter(articles.values()))
    title = article.get("title", "").strip()
    author = article.get("author", {}).get("name", "").strip()
    summary = article.get("excerpt", "").strip()
    tags = ["考研资料", "知乎专栏"]
    published_at = ""

    created = article.get("created")
    updated = article.get("updated")
    timestamp = updated or created
    if isinstance(timestamp, int) and timestamp > 0:
        published_at = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    content_html = article.get("content", "")
    if not content_html:
        raise ClipperError("知乎文章正文为空。")

    soup = BeautifulSoup(content_html, "html.parser")
    content_markdown = html_to_markdown_from_soup(soup)
    if not content_markdown:
        raise ClipperError("知乎文章正文解析失败。")

    return ClipResult(
        source="zhihu",
        title=title or f"知乎文章_{slug_from_url(url)}",
        author=author,
        url=url,
        published_at=published_at,
        tags=tags,
        summary=summary,
        content_markdown=content_markdown,
    )


def clip_zhihu(url: str, cookie: str = "") -> ClipResult:
    headers = {"Referer": "https://www.zhihu.com/"}
    if cookie:
        headers["Cookie"] = cookie
    try:
        html = fetch_text(url, headers=headers)
    except ClipperError as exc:
        if "HTTP 403" in str(exc):
            raise ClipperError(
                "知乎直连被拦截。请先设置 ZHIHU_COOKIE，或改用 import-html 导入浏览器保存的 HTML。"
            ) from exc
        raise
    state = extract_zhihu_state(html)
    return extract_zhihu_article_from_state(state, url)


def parse_zhihu_from_saved_html(path: Path) -> ClipResult:
    html = path.read_text(encoding="utf-8", errors="ignore")
    state = extract_zhihu_state(html)
    return extract_zhihu_article_from_state(state, str(path))


def parse_bilibili_from_saved_html(path: Path) -> ClipResult:
    html = path.read_text(encoding="utf-8", errors="ignore")
    state = extract_bilibili_state(html)
    detail = state.get("detail", {})
    basic = detail.get("basic", {})
    modules = detail.get("modules", [])
    content_markdown = bilibili_content_to_markdown(modules)
    if not content_markdown:
        raise ClipperError("本地 B 站 HTML 正文解析失败。")

    title = basic.get("title", "").replace(" - 哔哩哔哩", "").strip() or path.stem
    return ClipResult(
        source="bilibili",
        title=title,
        url=str(path),
        tags=["考研资料", "B站专栏", "本地导入"],
        content_markdown=content_markdown,
    )


def detect_source(source_hint: Optional[str], target: str) -> str:
    if source_hint:
        return source_hint.lower()

    lowered = target.lower()
    if "bilibili.com/read/" in lowered or "bilibili.com/opus/" in lowered:
        return "bilibili"
    if "zhihu.com" in lowered:
        return "zhihu"
    raise ClipperError("无法识别来源，请手动传入 --source。")


def render_frontmatter(result: ClipResult) -> str:
    tags = result.tags or ["考研资料"]
    lines = ["---"]
    lines.append(f'title: "{result.title.replace(chr(34), chr(39))}"')
    lines.append(f"source: {result.source}")
    if result.author:
        lines.append(f'author: "{result.author.replace(chr(34), chr(39))}"')
    if result.url:
        lines.append(f'url: "{result.url}"')
    if result.published_at:
        lines.append(f'published_at: "{result.published_at}"')
    lines.append(f'clipped_at: "{iso_now_local()}"')
    lines.append("tags:")
    for tag in tags:
        lines.append(f"  - {tag}")
    lines.append("---")
    return "\n".join(lines)


def render_markdown(result: ClipResult) -> str:
    body: List[str] = [render_frontmatter(result), "", f"# {result.title}", ""]
    meta_lines: List[str] = []
    if result.author:
        meta_lines.append(f"- 作者：{result.author}")
    if result.published_at:
        meta_lines.append(f"- 发布时间：{result.published_at}")
    if result.url:
        meta_lines.append(f"- 原文链接：{result.url}")
    if meta_lines:
        body.extend(meta_lines)
        body.append("")
    if result.summary:
        body.append("## 摘要")
        body.append("")
        body.append(normalize_whitespace(result.summary))
        body.append("")
    body.append("## 正文")
    body.append("")
    content = result.content_markdown.strip()
    normalized_title = normalize_whitespace(result.title)
    content_lines = content.splitlines()
    if content_lines:
        first_line = normalize_whitespace(content_lines[0].lstrip("#").strip())
        if first_line == normalized_title:
            content = "\n".join(content_lines[1:]).strip()
    body.append(content)
    body.append("")
    return "\n".join(body)


def write_result(result: ClipResult, output_dir: Path) -> Path:
    ensure_output_dir(output_dir)
    filename = f"{sanitize_filename(result.title)}.md"
    destination = output_dir / filename
    base_name = destination.stem
    suffix = destination.suffix
    counter = 2
    while destination.exists():
        destination = output_dir / f"{base_name}_{counter}{suffix}"
        counter += 1
    destination.write_text(render_markdown(result), encoding="utf-8")
    return destination


def clip_target(target: str, source_hint: Optional[str], output_dir: Path) -> Tuple[ClipResult, Path]:
    source = detect_source(source_hint, target)
    if source == "bilibili":
        result = clip_bilibili(target)
    elif source == "zhihu":
        result = clip_zhihu(target, cookie=os.getenv("ZHIHU_COOKIE", ""))
    else:
        raise ClipperError(f"暂不支持来源: {source}")
    written = write_result(result, output_dir)
    return result, written


def import_html(path: Path, source_hint: str, output_dir: Path) -> Tuple[ClipResult, Path]:
    source = detect_source(source_hint, str(path))
    if source == "zhihu":
        result = parse_zhihu_from_saved_html(path)
    elif source == "bilibili":
        result = parse_bilibili_from_saved_html(path)
    else:
        raise ClipperError(f"暂不支持来源: {source}")
    written = write_result(result, output_dir)
    return result, written


def load_url_lines(path: Path) -> Iterable[str]:
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        yield line


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="考研资料网页采集器")
    subparsers = parser.add_subparsers(dest="command", required=True)

    clip_parser = subparsers.add_parser("clip", help="抓取单个网页链接")
    clip_parser.add_argument("target", help="文章链接")
    clip_parser.add_argument("--source", choices=["bilibili", "zhihu"], help="手动指定来源")
    clip_parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="输出目录，默认是 资料收集/网页剪藏",
    )

    batch_parser = subparsers.add_parser("batch", help="批量抓取链接列表")
    batch_parser.add_argument("file", help="文本文件路径，每行一个链接")
    batch_parser.add_argument("--source", choices=["bilibili", "zhihu"], help="批量模式下统一指定来源")
    batch_parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="输出目录，默认是 资料收集/网页剪藏",
    )

    import_parser = subparsers.add_parser("import-html", help="从本地保存的 HTML 导入")
    import_parser.add_argument("file", help="本地 HTML 文件")
    import_parser.add_argument("--source", required=True, choices=["bilibili", "zhihu"], help="来源类型")
    import_parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="输出目录，默认是 资料收集/网页剪藏",
    )

    return parser


def command_clip(args: argparse.Namespace) -> int:
    output_dir = Path(args.output)
    result, written = clip_target(args.target, args.source, output_dir)
    print(f"[成功] {result.source}: {result.title}")
    print(written)
    return 0


def command_batch(args: argparse.Namespace) -> int:
    output_dir = Path(args.output)
    source_hint = args.source
    urls = list(load_url_lines(Path(args.file)))
    if not urls:
        raise ClipperError("链接列表为空。")

    failures: List[Tuple[str, str]] = []
    success_count = 0
    for url in urls:
        try:
            result, written = clip_target(url, source_hint, output_dir)
            success_count += 1
            print(f"[成功] {result.source}: {result.title}")
            print(written)
        except Exception as exc:
            failures.append((url, str(exc)))
            print(f"[失败] {url}")
            print(f"  原因: {exc}")

    print(f"\n完成：成功 {success_count} 篇，失败 {len(failures)} 篇")
    if failures:
        print("失败列表：")
        for url, reason in failures:
            print(f"- {url}")
            print(f"  {reason}")
        return 1
    return 0


def command_import_html(args: argparse.Namespace) -> int:
    output_dir = Path(args.output)
    result, written = import_html(Path(args.file), args.source, output_dir)
    print(f"[成功] {result.source}: {result.title}")
    print(written)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "clip":
            return command_clip(args)
        if args.command == "batch":
            return command_batch(args)
        if args.command == "import-html":
            return command_import_html(args)
        parser.print_help()
        return 1
    except ClipperError as exc:
        print(f"[错误] {exc}")
        return 1
    except Exception as exc:
        print(f"[异常] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
