"""Rename fieldnames PT→EN: Office Settings (idempotente)."""

from advocacia.patches.v16_0.rename_fields_pt_en import rename_doctype_columns


def execute():
	rename_doctype_columns("Office Settings")
