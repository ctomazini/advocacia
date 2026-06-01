"""Helpers para composição de títulos descritivos (Filosofia A)."""

import frappe
from frappe.utils import format_datetime, formatdate

TITLE_SEPARATOR = " — "


def get_cliente_nome(cliente):
	if not cliente:
		return ""
	return frappe.db.get_value("Cliente", cliente, "nome") or cliente


def join_title_parts(*parts):
	cleaned = [str(part).strip() for part in parts if part and str(part).strip()]
	return TITLE_SEPARATOR.join(cleaned)


def join_context_parts(*parts):
	return " ".join(str(part).strip() for part in parts if part and str(part).strip())


def fmt_date(value):
	if not value:
		return ""
	return formatdate(value)


def fmt_datetime(value):
	if not value:
		return ""
	return format_datetime(value)
