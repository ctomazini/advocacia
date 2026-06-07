import frappe
from frappe.tests.utils import FrappeTestCase


class TestAgentApi(FrappeTestCase):
	def test_get_active_cases_returns_list(self):
		from advocacia.advocacia.agent_api import get_active_cases

		result = get_active_cases()
		self.assertIsInstance(result, list)

	def test_get_active_cases_has_counts(self):
		from advocacia.advocacia.agent_api import get_active_cases

		result = get_active_cases()
		if result:
			case = result[0]
			self.assertIn("hearings", case)
			self.assertIn("deadlines", case)
			self.assertIn("tasks", case)

	def test_get_case_summary_not_found(self):
		from advocacia.advocacia.agent_api import get_case_summary

		with self.assertRaises(Exception):
			get_case_summary("NONEXISTENT-0000")

	def test_get_financial_overview_returns_dict(self):
		from advocacia.advocacia.agent_api import get_financial_overview

		result = get_financial_overview()
		self.assertIsInstance(result, dict)
		self.assertIn("overdue", result)
		self.assertIn("pending", result)
		self.assertIn("received_this_month", result)

	def test_get_financial_overview_has_amounts(self):
		from advocacia.advocacia.agent_api import get_financial_overview

		result = get_financial_overview()
		self.assertIn("overdue_amount", result)
		self.assertIn("received_amount", result)
