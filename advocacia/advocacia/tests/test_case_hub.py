import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from advocacia.advocacia.case_hub import get_case_counts, get_case_hub_data
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_hearing,
	create_test_legal_case,
	create_test_prazo,
	create_test_registro_atos,
)


class TestCaseHub(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_hub_returns_all_sections(self):
		case = create_test_legal_case()
		create_test_hearing(servico=case.name)

		data = get_case_hub_data(case.name)

		for key in (
			"phases",
			"hearings",
			"deadlines",
			"tasks",
			"communications",
			"service_records",
			"time_entries",
			"document_kits",
		):
			self.assertIn(key, data)

	def test_hub_hearings_match_db(self):
		case = create_test_legal_case()
		create_test_hearing(servico=case.name)
		create_test_hearing(servico=case.name)

		data = get_case_hub_data(case.name)

		self.assertEqual(len(data["hearings"]), 2)

	def test_hub_phases_current_only(self):
		case = create_test_legal_case()
		phase_name = f"Fase Hub {_uid_suffix()}"
		frappe.get_doc(
			{"doctype": "Case Phase", "case_phase_name": phase_name, "sort_order": 1}
		).insert(ignore_permissions=True)
		frappe.db.set_value("Legal Case", case.name, "case_phase", phase_name)

		data = get_case_hub_data(case.name)

		self.assertEqual(len(data["phases"]), 1)
		self.assertTrue(data["phases"][0]["is_current"])
		self.assertEqual(data["phases"][0]["case_phase_name"], phase_name)

	def test_financial_only_for_manager(self):
		case = create_test_legal_case()
		create_test_acordo(servico=case.name, num_parcelas=2)

		data = get_case_hub_data(case.name)

		if "Advocacia Manager" in frappe.get_roles():
			self.assertIn("financial", data)
			self.assertIsInstance(data["financial"], dict)
			self.assertGreaterEqual(len(data["financial"]["installments"]), 2)
		else:
			self.assertIsNone(data["financial"])

	def test_hub_deadlines_urgency(self):
		case = create_test_legal_case()
		create_test_prazo(servico=case.name, due_date=add_days(today(), -5), status="Pendente")

		data = get_case_hub_data(case.name)
		overdue = [row for row in data["deadlines"] if row["urgency"] == "overdue"]
		self.assertGreater(len(overdue), 0)

	def test_service_records_include_act_count(self):
		case = create_test_legal_case()
		create_test_registro_atos(servico=case.name)

		data = get_case_hub_data(case.name)

		self.assertEqual(len(data["service_records"]), 1)
		self.assertGreaterEqual(data["service_records"][0]["act_count"], 1)

	def test_get_case_counts_returns_keys(self):
		case = create_test_legal_case()
		counts = get_case_counts(case.name)

		base_keys = [
			"phases",
			"hearings",
			"deadlines",
			"tasks",
			"communications",
			"service_records",
			"time_entries",
			"document_kits",
		]
		for key in base_keys:
			self.assertIn(key, counts)

		if "Advocacia Manager" in frappe.get_roles():
			for key in ("installments", "payments", "court_costs", "fee_agreements"):
				self.assertIn(key, counts)

	def test_installment_count_via_join(self):
		if "Advocacia Manager" not in frappe.get_roles():
			return

		case = create_test_legal_case()
		create_test_acordo(servico=case.name, num_parcelas=3)

		counts = get_case_counts(case.name)

		self.assertEqual(counts["installments"], 3)
		self.assertGreaterEqual(counts["fee_agreements"], 1)


def _uid_suffix():
	return frappe.generate_hash(length=6)
