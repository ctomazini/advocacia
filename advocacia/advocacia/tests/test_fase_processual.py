import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


class TestCasePhase(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create(self):
		nome = _uid("Fase Inicial")
		doc = frappe.get_doc(
			{
				"doctype": "Case Phase",
				"case_phase_name": nome,
				"sort_order": 10,
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Case Phase", doc.name))
		self.assertEqual(doc.sort_order, 10)

	def test_read_and_update(self):
		nome = _uid("Fase Update")
		doc = frappe.get_doc(
			{"doctype": "Case Phase", "case_phase_name": nome, "sort_order": 1}
		).insert(ignore_permissions=True)
		loaded = frappe.get_doc("Case Phase", doc.name)
		loaded.sort_order = 99
		loaded.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Case Phase", doc.name, "sort_order"), 99)

	def test_required_case_phase_name_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{"doctype": "Case Phase", "sort_order": 5}
			).insert(ignore_permissions=True)

	def test_case_phase_name_duplicado_falha(self):
		nome = _uid("Fase Dup")
		frappe.get_doc(
			{"doctype": "Case Phase", "case_phase_name": nome, "sort_order": 1}
		).insert(ignore_permissions=True)
		with self.assertRaises((DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{"doctype": "Case Phase", "case_phase_name": nome, "sort_order": 2}
			).insert(ignore_permissions=True)
