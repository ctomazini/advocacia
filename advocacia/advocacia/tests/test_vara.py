import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


class TestCourtBranch(FrappeTestCase):
	def setUp(self):
		self.jurisdiction = frappe.get_doc(
			{
				"doctype": "Jurisdiction",
				"jurisdiction_name": _uid("Jurisdiction Court Branch"),
				"uf": "RS",
			}
		).insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.rollback()

	def test_create(self):
		nome = _uid("1ª Court Branch Cível")
		doc = frappe.get_doc(
			{
				"doctype": "Court Branch",
				"court_branch_name": nome,
				"jurisdiction": self.jurisdiction.name,
				"court_type": "Cível",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Court Branch", doc.name))
		self.assertEqual(doc.jurisdiction, self.jurisdiction.name)

	def test_read_and_update(self):
		nome = _uid("Court Branch Update")
		doc = frappe.get_doc(
			{
				"doctype": "Court Branch",
				"court_branch_name": nome,
				"jurisdiction": self.jurisdiction.name,
				"court_type": "Criminal",
			}
		).insert(ignore_permissions=True)
		loaded = frappe.get_doc("Court Branch", doc.name)
		self.assertEqual(loaded.court_type, "Criminal")

		loaded.court_type = "Família"
		loaded.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Court Branch", doc.name, "court_type"), "Família")

	def test_required_court_branch_name_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{"doctype": "Court Branch", "jurisdiction": self.jurisdiction.name, "court_type": "Cível"}
			).insert(ignore_permissions=True)

	def test_required_comarca_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{"doctype": "Court Branch", "court_branch_name": _uid("Sem Jurisdiction"), "court_type": "Cível"}
			).insert(ignore_permissions=True)

	def test_court_branch_name_duplicado_falha(self):
		nome = _uid("Court Branch Dup")
		frappe.get_doc(
			{
				"doctype": "Court Branch",
				"court_branch_name": nome,
				"jurisdiction": self.jurisdiction.name,
				"court_type": "Cível",
			}
		).insert(ignore_permissions=True)
		with self.assertRaises((DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{
					"doctype": "Court Branch",
					"court_branch_name": nome,
					"jurisdiction": self.jurisdiction.name,
					"court_type": "Trabalho",
				}
			).insert(ignore_permissions=True)
