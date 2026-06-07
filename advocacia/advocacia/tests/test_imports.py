import importlib
import json
import os
import pkgutil
from pathlib import Path

import advocacia
import frappe
from frappe.model.base_document import get_controller
from frappe.tests.utils import FrappeTestCase


class TestImports(FrappeTestCase):
	def test_all_modules_import(self):
		"""Import quebrado impede @frappe.whitelist() de registrar → 403 na UI."""
		falhas = []
		for _finder, name, _ispkg in pkgutil.walk_packages(advocacia.__path__, "advocacia."):
			if ".tests" in name or name.endswith(".test_setup"):
				continue
			try:
				importlib.import_module(name)
			except Exception as e:
				falhas.append(f"{name}: {e!r}")
		self.assertEqual(falhas, [], f"Módulos com import quebrado: {falhas}")

	def test_all_doctype_controllers_resolve(self):
		"""get_controller falha se o nome da classe não bate com o DocType."""
		dt_dir = Path(__file__).resolve().parents[1] / "doctype"
		falhas = []
		for folder in sorted(os.listdir(dt_dir)):
			json_path = dt_dir / folder / f"{folder}.json"
			if not json_path.is_file():
				continue
			meta = json.loads(json_path.read_text())
			dt = meta["name"]
			expected = dt.replace(" ", "").replace("-", "")
			try:
				controller = get_controller(dt)
				if controller.__name__ != expected:
					falhas.append(
						f"{dt}: esperado {expected!r}, encontrado {controller.__name__!r}"
					)
			except Exception as e:
				falhas.append(f"{dt}: {e!r}")
		self.assertEqual(falhas, [], f"Controllers quebrados: {falhas}")

	def test_whitelisted_modules_import_cleanly(self):
		"""Módulos com @frappe.whitelist() citados nos bugs reportados."""
		modules = [
			"advocacia.advocacia.documentos",
			"advocacia.advocacia.doctype.time_entry.time_entry",
			"advocacia.advocacia.doctype.document_kit.document_kit",
		]
		for mod in modules:
			with self.subTest(module=mod):
				importlib.import_module(mod)
				self.assertTrue(frappe.get_attr(mod))
