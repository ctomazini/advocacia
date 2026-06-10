import frappe
from frappe.tests import IntegrationTestCase

from advocacia.advocacia.setup.print_formats import (
	PRINT_FORMAT_NAMES,
	_REPORT_PRINT_FORMATS,
	ensure_advocacia_print_formats,
)


class TestReportPrintFormats(IntegrationTestCase):
	def test_print_formats_exist_after_setup(self):
		ensure_advocacia_print_formats()

		for spec in _REPORT_PRINT_FORMATS:
			self.assertTrue(
				frappe.db.exists("Print Format", spec["name"]),
				msg=f"Missing print format: {spec['name']}",
			)
			pf = frappe.get_doc("Print Format", spec["name"])
			self.assertEqual(pf.print_format_for, "Report")
			self.assertEqual(pf.report, spec["report"])
			self.assertEqual(pf.print_format_type, "JS")
			self.assertIn("adv-rpt-print", pf.html or "")
			self.assertIn("adv_office", pf.html or "")

	def test_print_formats_idempotent(self):
		ensure_advocacia_print_formats()
		count1 = frappe.db.count("Print Format", {"module": "Advocacia"})
		ensure_advocacia_print_formats()
		count2 = frappe.db.count("Print Format", {"module": "Advocacia"})
		self.assertEqual(count1, count2)
		self.assertGreaterEqual(count1, len(PRINT_FORMAT_NAMES))
