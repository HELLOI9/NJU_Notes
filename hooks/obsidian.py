"""把 Obsidian 风格的 markdown 在构建时转换成 MkDocs Material 能渲染的形式。

笔记本体保持 Obsidian 原生写法，转换只发生在 `mkdocs build` 期间。

目前处理：
    [[笔记]] / [[笔记|别名]] / [[笔记#标题]]      -> 站内链接
    ![[图片.png]] / ![[图片.png|382]]            -> 图片（支持宽度或 宽x高）
    > [!note] 标题  （后续 > 行）                 -> !!! note "标题"
    %% 注释 %%                                   -> 删除（可跨行）
    $$公式$$ / 表格                               -> 自动补空行并拆成独占一行的块，
                                                   否则 Python-Markdown 会把它当普通段落文字

围栏代码块（``` / ~~~）与行内代码（`...`）内的内容一律原样保留。

在 mkdocs.yml 中启用：
    hooks:
      - hooks/obsidian.py
"""

from __future__ import annotations

import posixpath
import re
from urllib.parse import quote

# [[目标#锚点|别名]]，前面的 ! 表示嵌入
WIKI_RE = re.compile(
    r"(?P<embed>!)?\[\[(?P<target>[^\]|#\n]+?)(?:#(?P<anchor>[^\]|\n]+?))?(?:\|(?P<alias>[^\]\n]*?))?\]\]"
)

# > [!note] / > [!warning]- 标题
CALLOUT_RE = re.compile(
    r"^(?P<indent>[ \t]*)>[ \t]*\[!(?P<kind>[A-Za-z]+)\](?P<fold>[+-])?[ \t]*(?P<title>.*)$"
)

# %% 注释 %%（可跨行）
COMMENT_RE = re.compile(r"%%(?:(?!%%)[\s\S])*?%%")

# 围栏代码块
FENCE_RE = re.compile(r"^[ \t]*(?P<fence>`{3,}|~{3,})")

# 行内代码
CODE_SPAN_RE = re.compile(r"(?P<ticks>`+)(?:(?!(?P=ticks)).)+?(?P=ticks)")

# Obsidian callout 类型 -> Material admonition 类型
CALLOUT_KINDS = {
    "note": "note",
    "abstract": "abstract",
    "summary": "abstract",
    "tldr": "abstract",
    "info": "info",
    "todo": "info",
    "tip": "tip",
    "hint": "tip",
    "important": "tip",
    "success": "success",
    "check": "success",
    "done": "success",
    "question": "question",
    "help": "question",
    "faq": "question",
    "warning": "warning",
    "caution": "warning",
    "attention": "warning",
    "failure": "failure",
    "fail": "failure",
    "missing": "failure",
    "danger": "danger",
    "error": "danger",
    "bug": "bug",
    "example": "example",
    "quote": "quote",
    "cite": "quote",
}

_notes: dict[str, str] = {}
_assets: dict[str, str] = {}


def on_files(files, config):
    """建立「笔记名 / 附件名 -> docs 内路径」索引，供下面的替换使用。"""
    _notes.clear()
    _assets.clear()
    for f in files:
        if f.is_documentation_page():
            stem = posixpath.splitext(f.src_path)[0]
            _notes.setdefault(posixpath.basename(stem), f.src_path)
            _notes.setdefault(stem, f.src_path)
        else:
            _assets.setdefault(posixpath.basename(f.src_path), f.src_path)
    return files


def on_page_markdown(markdown, page, config, files):
    out = []
    for is_code, segment in _segments(markdown):
        out.append(segment if is_code else _transform_block(segment, page))
    return "".join(out)


def _segments(markdown: str):
    """按围栏代码块把文档切成 (是否代码块, 文本) 片段。"""
    segments: list[tuple[bool, str]] = []
    buf: list[str] = []
    in_fence = False
    fence_char = ""

    for line in markdown.splitlines(keepends=True):
        fence = FENCE_RE.match(line)
        if fence is not None and not in_fence:
            if buf:
                segments.append((False, "".join(buf)))
                buf = []
            in_fence, fence_char = True, fence.group("fence")[0]
        elif fence is not None and in_fence and fence.group("fence")[0] == fence_char:
            buf.append(line)
            segments.append((True, "".join(buf)))
            buf = []
            in_fence = False
            continue
        buf.append(line)

    if buf:
        segments.append((in_fence, "".join(buf)))
    return segments


def _strip_comments(text: str) -> str:
    """删除 %% 注释 %%（可跨行），但跳过行内代码里的内容。"""
    protected: list[tuple[int, int]] = []
    offset = 0
    for line in text.split("\n"):
        for match in CODE_SPAN_RE.finditer(line):
            protected.append((offset + match.start(), offset + match.end()))
        offset += len(line) + 1

    out: list[str] = []
    pos = 0
    for match in COMMENT_RE.finditer(text):
        if any(start < match.end() and match.start() < end for start, end in protected):
            continue
        out.append(text[pos:match.start()])
        pos = match.end()
    out.append(text[pos:])
    return "".join(out)


def _transform_block(text: str, page) -> str:
    """处理非代码片段：注释、callout、wiki 链接，并规范化块级语法。"""
    lines = _transform_lines(_strip_comments(text).split("\n"), page)
    lines = _split_inline_tables(lines)
    return "\n".join(_pad_blocks(_split_math_lines(lines)))


def _transform_lines(lines: list[str], page) -> list[str]:
    """逐行处理 callout 与 wiki 链接。"""
    out: list[str] = []
    in_callout = False
    callout_indent = ""

    for line in lines:
        if in_callout and re.match(r"^[ \t]*>", line):
            body = re.sub(r"^[ \t]*>[ \t]?", "", line)
            out.append(
                f"{callout_indent}    {_transform_links(body, page)}" if body.strip() else ""
            )
            continue
        in_callout = False

        callout = CALLOUT_RE.match(line)
        if callout is not None:
            marker = {"-": "???", "+": "???+"}.get(callout.group("fold") or "", "!!!")
            kind = CALLOUT_KINDS.get(callout.group("kind").lower(), "note")
            title = callout.group("title").strip()
            out.append(callout.group("indent") + f"{marker} {kind}" + (f' "{title}"' if title else ""))
            callout_indent = callout.group("indent")
            in_callout = True
            continue

        out.append(_transform_links(line, page))

    return out


# 整行就是一个块级公式
MATH_BLOCK_LINE = re.compile(r"^\s*\$\$.+\$\$\s*$")
# 行内的 $$ 分隔符（\$ 是转义的美元，不算分隔符）
MATH_DELIM = re.compile(r"(?<!\\)\$\$")
TABLE_ROW = re.compile(r"^\s*\|")
# 表格的分隔行（|---|:--:| 之类，必须含 | 才算表格，否则是 --- 水平线）
TABLE_SEP_ROW = re.compile(r"^\s*\|?[\s:|-]*-{3,}[\s:|-]*\|?\s*$")


def _split_inline_tables(lines: list[str]) -> list[str]:
    """把「正文文字直接接表头 | A | B |」拆成两行——不拆的话表格不会渲染。"""
    out: list[str] = []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if line.strip().startswith("|") or "|" not in line:
            out.append(line)
            continue
        if "|" not in nxt or not TABLE_SEP_ROW.match(nxt):
            out.append(line)
            continue

        cut = next(
            (m.start() for m in re.finditer(r"\|", line) if line[m.start():].count("|") >= 2),
            None,
        )
        if cut is None or not line[:cut].strip():
            out.append(line)
            continue

        out.append(line[:cut].rstrip())
        out.append(line[cut:].strip())

    return out


def _split_math_lines(lines: list[str]) -> list[str]:
    """把「一行里混着文字和 $$公式$$」拆成各自独占一行的块。"""
    out: list[str] = []
    in_math = False

    for line in lines:
        stripped = line.strip()
        if in_math:                     # 多行公式内部，原样保留
            out.append(line)
            if stripped == "$$":
                in_math = False
            continue
        if stripped == "$$":            # 多行公式的开头
            out.append(line)
            in_math = True
            continue
        out.extend(_split_line_math(line))

    return out


def _split_line_math(line: str) -> list[str]:
    """拆一行里的公式；没有成对公式（或整行本来就是一个公式）时原样返回。"""
    protected = [(m.start(), m.end()) for m in CODE_SPAN_RE.finditer(line)]
    marks = [
        m.start()
        for m in MATH_DELIM.finditer(line)
        if not any(start < m.start() < end for start, end in protected)
    ]
    if len(marks) < 2 or len(marks) % 2:
        return [line]
    if len(marks) == 2 and not line[:marks[0]].strip() and not line[marks[1] + 2:].strip():
        return [line]

    indent = line[: len(line) - len(line.lstrip())]
    pieces: list[str] = []
    pos = 0
    for i in range(0, len(marks), 2):
        start, end = marks[i], marks[i + 1] + 2
        if before := line[pos:start].strip():
            pieces.append(before)
        pieces.append(line[start:end].strip())
        pos = end
    if tail := line[pos:].strip():
        pieces.append(tail)

    out: list[str] = []
    for piece in pieces:
        if out:
            out.append("")
        out.append(indent + piece)
    return out


def _pad_blocks(lines: list[str]) -> list[str]:
    """给 $$公式$$、表格补前后空行；缺少空行时 Python-Markdown 不会当块级语法解析。"""
    out: list[str] = []
    in_math = False
    prev = ""

    for line in lines:
        stripped = line.strip()

        if in_math:                     # 多行公式内部不插空行
            out.append(line)
            if stripped == "$$":
                in_math = False
                prev = "math"
            continue

        if not stripped:
            out.append(line)
            prev = ""
            continue

        if MATH_BLOCK_LINE.match(line) or stripped == "$$":
            if prev:
                out.append("")
            out.append(line)
            in_math = stripped == "$$" and not MATH_BLOCK_LINE.match(line)
            prev = "math"
            continue

        if TABLE_ROW.match(line):
            if prev and prev != "table":
                out.append("")
            out.append(line)
            prev = "table"
            continue

        if prev in ("math", "table"):   # 公式/表格后面也要留空行
            out.append("")
        out.append(line)
        prev = "text"

    return out


def _transform_links(line: str, page) -> str:
    """替换 wiki 链接，但跳过行内代码。"""
    out: list[str] = []
    pos = 0
    for match in CODE_SPAN_RE.finditer(line):
        out.append(WIKI_RE.sub(lambda m: _wiki(m, page), line[pos:match.start()]))
        out.append(match.group(0))
        pos = match.end()
    out.append(WIKI_RE.sub(lambda m: _wiki(m, page), line[pos:]))
    return "".join(out)


def _wiki(match: re.Match, page) -> str:
    """把一条 [[...]] 语法转成普通 markdown 链接或图片。"""
    target = match.group("target").strip()
    anchor = (match.group("anchor") or "").strip()
    alias = (match.group("alias") or "").strip()

    note = _notes.get(target) or _notes.get(posixpath.splitext(target)[0])
    if note is not None:
        text = alias or posixpath.basename(posixpath.splitext(target)[0])
        url = _relative(page, note)
        if anchor:
            url += f"#{anchor}"
        return f"[{text}](<{url}>)"

    asset = _assets.get(posixpath.basename(target))
    if asset is not None:
        url = _relative(page, asset)
        if match.group("embed"):
            return f"![{posixpath.basename(target)}](<{url}>){_size(alias)}"
        return f"[{alias or posixpath.basename(target)}](<{url}>)"

    # 找不到对应文件时原样保留，方便在构建产物里发现写错的链接
    return match.group(0)


def _size(alias: str) -> str:
    """把 Obsidian 的 |382 或 |382x200 转成 attr_list 的尺寸属性。"""
    if not alias:
        return ""
    parts = alias.lower().split("x")
    if len(parts) == 2 and all(p.strip().isdigit() for p in parts):
        return f'{{ width="{parts[0].strip()}" height="{parts[1].strip()}" }}'
    if alias.isdigit():
        return f'{{ width="{alias}" }}'
    return ""


def _relative(page, src_path: str) -> str:
    """算出目标文件相对当前页面源目录的路径（MkDocs 会据此重写成产出 URL）。"""
    base = posixpath.dirname(page.file.src_path)
    rel = posixpath.relpath(src_path, base) if base else src_path
    # 括号保留原样（markdown 里用 <> 包住即可），空格转义成 %20
    return quote(rel, safe="/()")
