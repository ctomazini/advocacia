import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


class TestVara(FrappeTestCase):
	def setUp(self):
		self.comarca = frappe.get_doc(
			{
				"doctype": "Comarca",
				"comarca_name": _uid("Comarca Vara"),
				"uf": "RS",
			}
		).insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.rollback()

	def test_create(self):
		nome = _uid("1ª Vara Cível")
		doc = frappe.get_doc(
			{
				"doctype": "Vara",
				"vara_name": nome,
				"comarca": self.comarca.name,
				"court_type": "Cível",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Vara", doc.name))
		self.assertEqual(doc.comarca, self.comarca.name)

	def test_read_and_update(self):
		nome = _uid("Vara Update")
		doc = frappe.get_doc(
			{
				"doctype": "Vara",
				"vara_name": nome,
				"comarca": self.comarca.name,
				"court_type": "Criminal",
			}
		).insert(ignore_permissions=True)
		loaded = frappe.get_doc("Vara", doc.name)
		self.assertEqual(loaded.court_type, "Criminal")

		loaded.court_type = "Família"
		loaded.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Vara", doc.name, "court_type"), "Família")

	def test_required_vara_name_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{"doctype": "Vara", "comarca": self.comarca.name, "court_type": "Cível"}
			).insert(ignore_permissions=True)

	def test_required_comarca_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{"doctype": "Vara", "vara_name": _uid("Sem Comarca"), "court_type": "Cível"}
			).insert(ignore_permissions=True)

	def test_vara_name_duplicado_falha(self):
		nome = _uid("Vara Dup")
		frappe.get_doc(
			{
				"doctype": "Vara",
				"vara_name": nome,
				"comarca": self.comarca.name,
				"court_type": "Cível",
			}
		).insert(ignore_permissions=True)
		with self.assertRaises((DuplicateEntryError, frappe.UniqueValidationError)):
			frappe.get_doc(
				{
					"doctype": "Vara",
					"vara_name": nome,
					"comarca": self.comarca.name,
					"court_type": "Trabalho",
				}
			).insert(ignore_permissions=True)
