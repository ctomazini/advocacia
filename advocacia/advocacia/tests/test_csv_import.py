import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia import hooks as advocacia_hooks
from advocacia.advocacia.setup.permissions import setup_permissions

IMPORTABLE_DOCTYPES = (
	"Client",
	"Legal Case",
	"Jurisdiction",
	"Case Phase",
	"Court",
)


class TestCsvImport(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		setup_permissions()

	def tearDown(self):
		frappe.db.rollback()

	def test_importable_doctypes_hook(self):
		self.assertEqual(
			advocacia_hooks.importable_doctypes,
			list(IMPORTABLE_DOCTYPES),
		)
		hook_values = frappe.get_hooks("importable_doctypes", app_name="advocacia")
		for doctype in IMPORTABLE_DOCTYPES:
			self.assertIn(doctype, hook_values)

	def test_allow_import_on_doctypes(self):
		for doctype in IMPORTABLE_DOCTYPES:
			self.assertEqual(
				frappe.get_meta(doctype).allow_import,
				1,
				msg=f"{doctype} deve permitir importação CSV",
			)

	def test_import_permission_administrator(self):
		self.assertTrue(frappe.has_permission("Client", "import", user="Administrator"))

	def test_import_permission_advocacia_manager(self):
		user_email = f"csv_import_{frappe.generate_hash(length=6)}@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "CSV",
					"last_name": "Import",
					"send_welcome_email": 0,
					"roles": [{"role": "Advocacia Manager"}],
				}
			).insert(ignore_permissions=True)

		self.assertTrue(frappe.has_permission("Client", "import", user=user_email))
