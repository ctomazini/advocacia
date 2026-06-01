import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


class TestTribunal(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_create(self):
		nome = _uid("Tribunal Justiça RS")
		sigla = _unique_sigla("TJ")
		doc = frappe.get_doc(
			{
				"doctype": "Tribunal",
				"tribunal_name": nome,
				"abbreviation": sigla,
				"jurisdiction": "Estadual",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Tribunal", doc.name))
		self.assertEqual(doc.jurisdiction, "Estadual")

	def test_read_and_update(self):
		nome = _uid("Tribunal Read")
		sigla = _unique_sigla("TR")
		doc = frappe.get_doc(
			{
				"doctype": "Tribunal",
				"tribunal_name": nome,
				"abbreviation": sigla,
				"jurisdiction": "Federal",
			}
		).insert(ignore_permissions=True)
		loaded = frappe.get_doc("Tribunal", doc.name)
		loaded.jurisdiction = "Trabalho"
		loaded.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Tribunal", doc.name, "jurisdiction"), "Trabalho")

	def test_required_tribunal_name_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Tribunal",
					"abbreviation": _unique_sigla("X"),
					"jurisdiction": "Estadual",
				}
			).insert(ignore_permissions=True)

	def test_abbreviation_duplicado_falha(self):
		sigla = _unique_sigla("DU")
		frappe.get_doc(
			{
				"doctype": "Tribunal",
				"tribunal_name": _uid("Tribunal A"),
				"abbreviation": sigla,
				"jurisdiction": "Estadual",
			}
		).insert(ignore_permissions=True)
		with self.assertRaises((frappe.DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{
					"doctype": "Tribunal",
					"tribunal_name": _uid("Tribunal B"),
					"abbreviation": sigla,
					"jurisdiction": "Federal",
				}
			).insert(ignore_permissions=True)


def _unique_sigla(prefix="TJ"):
	return f"{prefix}{frappe.generate_hash(length=10)}"
