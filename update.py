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
        if entry.is_dir():
            children = build_nav_tree(entry.path)
            if not children:
                continue
            first_key = list(children[0].keys())[0]
            first_val = list(children[0].values())[0]

            # A directory with a single markdown page doesn't need an extra level.
            if len(children) == 1 and isinstance(first_val, str):
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
