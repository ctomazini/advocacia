import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


class TestComarca(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create(self):
		nome = _uid("Comarca POA")
		doc = frappe.get_doc(
			{
				"doctype": "Comarca",
				"comarca_name": nome,
				"uf": "RS",
				"city": "Porto Alegre",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Comarca", doc.name))
		self.assertEqual(doc.comarca_name, nome)
		self.assertEqual(doc.uf, "RS")

	def test_read_and_update(self):
		nome = _uid("Comarca Read")
		doc = frappe.get_doc(
			{"doctype": "Comarca", "comarca_name": nome, "uf": "SP"}
		).insert(ignore_permissions=True)
		loaded = frappe.get_doc("Comarca", doc.name)
		self.assertEqual(loaded.comarca_name, nome)

		loaded.city = "São Paulo"
		loaded.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Comarca", doc.name, "city"), "São Paulo")

	def test_required_comarca_name_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc({"doctype": "Comarca", "uf": "RS"}).insert(ignore_permissions=True)

	def test_comarca_name_duplicado_falha(self):
		nome = _uid("Comarca Dup")
		frappe.get_doc(
			{"doctype": "Comarca", "comarca_name": nome, "uf": "RS"}
		).insert(ignore_permissions=True)
		with self.assertRaises((DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{"doctype": "Comarca", "comarca_name": nome, "uf": "SC"}
			).insert(ignore_permissions=True)
