import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.report_visuals import (
	CASH_IN_OUT,
	HONORARIOS_CHART_COLORS,
	REPORT_COLORS,
	bar_chart,
	currency_summary,
	donut_chart,
	month_label,
)


class TestReportVisuals(FrappeTestCase):
	def test_palette_has_semantic_colors(self):
		self.assertIn("green", REPORT_COLORS)
		self.assertIn("red", REPORT_COLORS)
		self.assertEqual(len(CASH_IN_OUT), 2)
		self.assertEqual(len(HONORARIOS_CHART_COLORS), 3)

	def test_month_label(self):
		self.assertEqual(month_label("2026-03-15"), "Mar/2026")

	def test_bar_chart(self):
		chart = bar_chart(["A"], [{"name": "Série", "values": [1]}], CASH_IN_OUT)
		self.assertEqual(chart["type"], "bar")
		self.assertEqual(chart["colors"], CASH_IN_OUT)

	def test_donut_chart(self):
		chart = donut_chart(["X"], [10], HONORARIOS_CHART_COLORS)
		self.assertEqual(chart["type"], "donut")

	def test_currency_summary(self):
		row = currency_summary(100.5, "Total", "Green")
		self.assertEqual(row["datatype"], "Currency")
		self.assertEqual(row["indicator"], "Green")
