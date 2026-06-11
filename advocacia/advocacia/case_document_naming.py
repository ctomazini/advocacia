"""Composição de título para Case Document."""

from __future__ import annotations

import frappe


def compose_case_document_title(
	category: str,
	legal_case: str,
	version_label: str | None = None,
) -> str:
	case_title = frappe.db.get_value("Legal Case", legal_case, "title") if legal_case else ""
	case_title = case_title or legal_case or ""
	parts = [category or "Outro", case_title]
	if version_label and str(version_label).strip():
		parts.append(str(version_label).strip())
	return " — ".join(part for part in parts if part)
