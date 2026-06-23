#!/usr/bin/env python3
"""Append or refresh standardized doc footer on project markdown files."""

from __future__ import annotations

import re
from pathlib import Path

APP_VERSION = "1.1.0"
STAMP = f"**Última atualização:** 2026-06-23 23:24 UTC · **Versão do app:** {APP_VERSION}"
STAMP_RE = re.compile(r"\n\*\*Última atualização:\*\*[^\n]*\n?$")
ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {"node_modules", ".git"}


def iter_markdown_files() -> list[Path]:
	files: list[Path] = []
	for path in sorted(ROOT.rglob("*.md")):
		if any(part in SKIP_PARTS for part in path.parts):
			continue
		files.append(path)
	return files


def apply_stamp(text: str) -> str:
	body = STAMP_RE.sub("", text.rstrip())
	body = re.sub(r"\n{3,}", "\n\n", body)
	return f"{body}\n\n---\n\n{STAMP}\n"


def main() -> None:
	for path in iter_markdown_files():
		original = path.read_text(encoding="utf-8")
		updated = apply_stamp(original)
		if updated != original:
			path.write_text(updated, encoding="utf-8")
			print(f"stamped: {path.relative_to(ROOT)}")


if __name__ == "__main__":
	main()
