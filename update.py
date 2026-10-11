#!/usr/bin/env python3
"""Auto-update mkdocs.yml nav section based on docs/notes directory structure."""

import os
import yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
NOTES_DIR = os.path.join(DOCS_DIR, "notes")
MKDOCS_FILE = os.path.join(ROOT_DIR, "mkdocs.yml")


def build_nav_tree(directory):
    """Recursively build nav tree, paths relative to docs/."""
    items = []
    entries = sorted(os.scandir(directory), key=lambda e: (e.is_file(), e.name))
    for entry in entries:
        # MkDocs 不会构建以 "." 开头的目录/文件（如 .obsidian、.trash），
        # 写进 nav 只会产生失效链接。
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            children = build_nav_tree(entry.path)
            if not children:
                continue
            first_key = list(children[0].keys())[0]
            first_val = list(children[0].values())[0]

            # 目录下只有一个 md 文件、且没有更深的子目录时，才考虑省掉一层，
            # 且只有当「目录名足以代表这篇笔记」时才省：
            #   - index.md（目录自己的首页）
            #   - 笔记名以目录名开头（Chapter1/Chapter1.md、Chapter4/Chapter4-xxx.md）
            # 名字对不上时（Chapter4/LL(1)文法.md、Chap Lab/Lab2-协程.md）保留目录层，
            # 叶子显示笔记名，否则侧栏上根本看不到笔记叫什么。
            # 目录里还有子目录时一律不折叠，否则单链目录会被压成一条、丢掉层级。
            has_subdir = any(
                e.is_dir() and not e.name.startswith(".")
                for e in os.scandir(entry.path)
            )
            single_page = len(children) == 1 and isinstance(first_val, str) and not has_subdir
            label_is_page = first_key == "__index__" or first_key.startswith(entry.name)
            if single_page and label_is_page:
                items.append({entry.name: first_val})
            else:
                if first_key == "__index__":
                    children[0] = {"Overview": first_val}
                items.append({entry.name: children})
        elif entry.is_file() and entry.name.endswith(".md"):
            rel_path = os.path.relpath(entry.path, DOCS_DIR)
            label = os.path.splitext(entry.name)[0]
            if label == "index":
                items.insert(0, {"__index__": rel_path})
            else:
                items.append({label: rel_path})

    return items


def find_nav_block(content):
    """Return the start/end offsets for the top-level nav block in mkdocs.yml."""
    lines = content.splitlines(keepends=True)
    start_line = None

    for i, line in enumerate(lines):
        if line.startswith("nav:"):
            start_line = i
            break

    if start_line is None:
        return None, None

    end_line = len(lines)
    for i in range(start_line + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            continue

        # The nav block can contain top-level list items like "- Home: index.md".
        # Stop only when the next top-level mapping key begins.
        if not line.startswith((" ", "\t", "-")):
            end_line = i
            break

    start = sum(len(line) for line in lines[:start_line])
    end = sum(len(line) for line in lines[:end_line])
    return start, end


def update_mkdocs_nav():
    with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    notes_tree = build_nav_tree(NOTES_DIR)
    course_notes_nav = [{"Overview": "notes/index.md"}]
    for item in notes_tree:
        for key, val in item.items():
            if isinstance(val, str) and val == "notes/index.md":
                continue
            course_notes_nav.append({key: val})

    # Parse only the nav block so that !!python tags elsewhere remain untouched.
    nav_start, nav_end = find_nav_block(content)
    if nav_start is None:
        print("nav section not found in mkdocs.yml")
        return

    nav_block_str = content[nav_start:nav_end]
    nav_data = yaml.safe_load(nav_block_str)
    nav = nav_data.get("nav") or []

    for i, section in enumerate(nav):
        if "Course Notes" in section:
            nav[i] = {"Course Notes": course_notes_nav}
            break
    else:
        nav.append({"Course Notes": course_notes_nav})

    new_nav_yaml = yaml.dump({"nav": nav}, allow_unicode=True, default_flow_style=False, sort_keys=False)

    new_content = content[:nav_start] + new_nav_yaml + content[nav_end:]

    with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("nav updated successfully.")


if __name__ == "__main__":
    update_mkdocs_nav()
