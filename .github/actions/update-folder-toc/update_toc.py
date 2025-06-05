#!/usr/bin/env python3
"""
update_toc.py
-------------
Regenerates a bullet-point table of contents in <root>/README.md, listing the
FIRST-LEVEL sub-folders that contain their own README.md files.

Usage (inside a GitHub Action):
  env ROOT_DIR=<folder> python update_toc.py
"""

import os
import pathlib
import re
import sys

TAG = "<!-- AUTO-GENERATED TOC -->"            # delimiters in README

# --------------------------------------------------------------------------- #
# Locate the root directory passed in via environment variable
# --------------------------------------------------------------------------- #
try:
    root_dir = pathlib.Path(os.environ["ROOT_DIR"]).resolve()
except KeyError:
    sys.exit("ROOT_DIR environment variable not set")

readme_path = root_dir / "README.md"

# --------------------------------------------------------------------------- #
# If the folder itself has no README, just skip gracefully
# --------------------------------------------------------------------------- #
if not readme_path.exists():
    print(f"{readme_path} missing; skipping.")
    sys.exit(0)                # Success exit so the workflow continues

# --------------------------------------------------------------------------- #
# Gather entries: one line per sub-folder that has its own README
# --------------------------------------------------------------------------- #
entries = []
for sub in sorted(p for p in root_dir.iterdir() if p.is_dir()):
    child_readme = sub / "README.md"
    if child_readme.exists():
        # Use the first non-blank line (strip leading # if it’s a Markdown H1)
        with child_readme.open(encoding="utf-8") as fh:
            first_line = ""
            for line in fh:
                clean = line.strip()
                if clean:
                    first_line = clean.lstrip("#").strip()
                    break
        rel_link = child_readme.relative_to(root_dir)
        entries.append(f"- [{first_line}]({rel_link})")

if not entries:
    print(f"No sub-folder READMEs inside {root_dir}; nothing to update.")
    sys.exit(0)

toc_block = "\n".join(entries)

# --------------------------------------------------------------------------- #
# Inject or replace the TOC section between TAG markers
# --------------------------------------------------------------------------- #
pattern = re.compile(rf"{TAG}.*?{TAG}", flags=re.S)

with readme_path.open(encoding="utf-8") as fh:
    body = fh.read()

replacement = f"{TAG}\n\n{toc_block}\n\n{TAG}"
new_body = (
    pattern.sub(replacement, body) if pattern.search(body)
    else body.rstrip() + "\n\n" + replacement + "\n"
)

with readme_path.open("w", encoding="utf-8") as fh:
    fh.write(new_body)

print(f"Updated TOC in {readme_path}")
