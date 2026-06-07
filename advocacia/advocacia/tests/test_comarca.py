import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


class TestJurisdiction(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create(self):
		nome = _uid("Jurisdiction POA")
		doc = frappe.get_doc(
			{
				"doctype": "Jurisdiction",
				"jurisdiction_name": nome,
				"uf": "RS",
				"city": "Porto Alegre",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Jurisdiction", doc.name))
		self.assertEqual(doc.jurisdiction_name, nome)
		self.assertEqual(doc.uf, "RS")

	def test_read_and_update(self):
		nome = _uid("Jurisdiction Read")
		doc = frappe.get_doc(
			{"doctype": "Jurisdiction", "jurisdiction_name": nome, "uf": "SP"}
		).insert(ignore_permissions=True)
		loaded = frappe.get_doc("Jurisdiction", doc.name)
		self.assertEqual(loaded.jurisdiction_name, nome)

		loaded.city = "São Paulo"
		loaded.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Jurisdiction", doc.name, "city"), "São Paulo")

	def test_required_jurisdiction_name_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc({"doctype": "Jurisdiction", "uf": "RS"}).insert(ignore_permissions=True)

	def test_jurisdiction_name_duplicado_falha(self):
		nome = _uid("Jurisdiction Dup")
		frappe.get_doc(
			{"doctype": "Jurisdiction", "jurisdiction_name": nome, "uf": "RS"}
		).insert(ignore_permissions=True)
		with self.assertRaises((DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{"doctype": "Jurisdiction", "jurisdiction_name": nome, "uf": "SC"}
			).insert(ignore_permissions=True)
