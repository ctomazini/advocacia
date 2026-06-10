"""Rename fieldnames PT→EN: Case Communication (idempotente)."""

from advocacia.patches.v16_0.rename_fields_pt_en import rename_doctype_columns


def execute():
	rename_doctype_columns("Case Communication")
