import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.setup.print_formats import PRINT_FORMAT_NAMES, ensure_advocacia_print_formats
from advocacia.advocacia.setup.seed import (
	DEFAULT_CASE_PHASES,
	DEFAULT_DOCUMENT_CATEGORIES,
	ensure_seed_data,
)


class TestSeed(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_seed_idempotent(self):
		ensure_seed_data()
		count_after_first = frappe.db.count("Case Phase")
		ensure_seed_data()
		count_after_second = frappe.db.count("Case Phase")
		self.assertEqual(count_after_first, count_after_second)
		for phase_def in DEFAULT_CASE_PHASES:
			self.assertTrue(frappe.db.exists("Case Phase", phase_def["case_phase_name"]))
		for category_name in DEFAULT_DOCUMENT_CATEGORIES:
			self.assertTrue(frappe.db.exists("Document Category", category_name))


class TestPrintFormats(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		ensure_advocacia_print_formats()

	def tearDown(self):
		frappe.db.rollback()

	def test_print_formats_exist(self):
		for name in PRINT_FORMAT_NAMES:
			self.assertTrue(
				frappe.db.exists("Print Format", name),
				msg=f"Print Format {name} não encontrado — rode migrate",
			)

	def test_print_format_html_not_empty(self):
		for name in PRINT_FORMAT_NAMES:
			html = frappe.db.get_value("Print Format", name, "html")
			self.assertTrue(html and len(html.strip()) > 50, msg=f"{name} sem HTML")

	def test_sync_idempotent(self):
		ensure_advocacia_print_formats()
		for name in PRINT_FORMAT_NAMES:
			self.assertTrue(frappe.db.exists("Print Format", name))
