import frappe
from frappe.exceptions import PermissionError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.agent_api import (
	get_active_cases,
	get_case_summary,
	get_court_costs_by_type,
	get_financial_overview,
)
from advocacia.advocacia.tests.test_setup import create_test_court_cost, create_test_legal_case


class TestAgentApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_active_cases_returns_list(self):
		result = get_active_cases()
		self.assertIsInstance(result, list)

	def test_get_active_cases_has_counts_and_client_name(self):
		create_test_legal_case(status="Em andamento")
		result = get_active_cases()
		self.assertTrue(result)
		case = result[0]
		self.assertIn("hearings", case)
		self.assertIn("deadlines", case)
		self.assertIn("tasks", case)
		self.assertIn("client_name", case)

	def test_get_case_summary_not_found(self):
		with self.assertRaises(Exception):
			get_case_summary("NONEXISTENT-0000")

	def test_get_case_summary_financial_for_manager(self):
		case = create_test_legal_case(status="Em andamento")
		summary = get_case_summary(case.name)
		self.assertEqual(summary["name"], case.name)
		self.assertIn("client_name", summary)
		self.assertIn("fee_agreement_value", summary)
		self.assertIn("amount_receivable", summary)

	def test_get_court_costs_by_type(self):
		case = create_test_legal_case()
		create_test_court_cost(servico=case.name, amount=150, type="Taxa Judicial")
		result = get_court_costs_by_type(case.name)
		self.assertEqual(result["case"], case.name)
		self.assertGreaterEqual(result["total"], 150)
		self.assertTrue(result["categories"])

	def test_get_case_summary_redacts_financial_for_user(self):
		from advocacia.advocacia.setup.roles import create_roles

		create_roles()
		case = create_test_legal_case(status="Em andamento")

		user_email = f"agent_user_{frappe.generate_hash(length=6)}@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "Agent",
					"last_name": "User",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "Has Role",
				"parent": user_email,
				"parenttype": "User",
				"parentfield": "roles",
				"role": "Advocacia User",
			}
		).insert(ignore_permissions=True)

		frappe.set_user(user_email)
		try:
			summary = get_case_summary(case.name)
			self.assertNotIn("fee_agreement_value", summary)
			self.assertNotIn("amount_receivable", summary)
			self.assertTrue(summary.get("financial_restricted"))
		finally:
			frappe.set_user("Administrator")

	def test_get_court_costs_by_type_requires_manager(self):
		from advocacia.advocacia.setup.roles import create_roles

		create_roles()
		case = create_test_legal_case()

		user_email = f"agent_user2_{frappe.generate_hash(length=6)}@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "Agent",
					"last_name": "User2",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "Has Role",
				"parent": user_email,
				"parenttype": "User",
				"parentfield": "roles",
				"role": "Advocacia User",
			}
		).insert(ignore_permissions=True)

		frappe.set_user(user_email)
		try:
			with self.assertRaises(PermissionError):
				get_court_costs_by_type(case.name)
		finally:
			frappe.set_user("Administrator")

	def test_get_financial_overview_returns_dict(self):
		result = get_financial_overview()
		self.assertIsInstance(result, dict)
		self.assertIn("overdue", result)
		self.assertIn("pending", result)
		self.assertIn("received_this_month", result)

	def test_get_financial_overview_has_amounts(self):
		result = get_financial_overview()
		self.assertIn("overdue_amount", result)
		self.assertIn("received_amount", result)

	def test_permission_denied_without_access(self):
		user_email = f"agent_no_perm_{frappe.generate_hash(length=6)}@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "Agent",
					"last_name": "NoPerm",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user_email)
		try:
			with self.assertRaises(PermissionError):
				get_active_cases()
		finally:
			frappe.set_user("Administrator")
