import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.tests.test_setup import _uid


class TestDocumentCategory(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud(self):
		name = _uid("Petição Cat")
		doc = frappe.get_doc(
			{"doctype": "Document Category", "category_name": name}
		).insert(ignore_permissions=True)
		self.assertEqual(doc.name, name)

	def test_category_name_required(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc({"doctype": "Document Category"}).insert(ignore_permissions=True)
