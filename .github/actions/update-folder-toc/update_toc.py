#!/usr/bin/env python3
import os, pathlib, re, sys

root = pathlib.Path(os.environ["ROOT_DIR"]).resolve()
readme_path = root / "README.md"
if not readme_path.exists():
    sys.exit(f"{readme_path} missing; skipping.")

entries = []
for sub in sorted(p for p in root.iterdir() if p.is_dir()):
    md = sub / "README.md"
    if md.exists():
        with md.open(encoding="utf-8") as fh:
            title = fh.readline().strip().lstrip("#").strip()
        rel_link = md.relative_to(root)
        entries.append(f"- [{title}]({rel_link})")

if not entries:
    sys.exit(f"No sub-folder READMEs in {root}; nothing to do.")

toc_block = "\n".join(entries)
tag = "<!-- AUTO-GENERATED TOC -->"
pat = re.compile(rf"{tag}.*?{tag}", re.S)

with readme_path.open(encoding="utf-8") as fh:
    body = fh.read()

replacement = f"{tag}\n\n{toc_block}\n\n{tag}"
new_body = pat.sub(replacement, body) if pat.search(body) else body.rstrip() + "\n\n" + replacement + "\n"

with readme_path.open("w", encoding="utf-8") as fh:
    fh.write(new_body)
