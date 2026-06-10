"""Rename fieldnames PT→EN: Hearing (idempotente)."""

from advocacia.patches.v16_0.rename_fields_pt_en import rename_doctype_columns


def execute():
	rename_doctype_columns("Hearing")
