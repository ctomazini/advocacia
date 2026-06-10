import frappe
from frappe.tests import IntegrationTestCase


class TestBootSession(IntegrationTestCase):
	def test_boot_session_injects_adv_office(self):
		from advocacia.boot import boot_session

		bootinfo = frappe._dict()
		boot_session(bootinfo)

		self.assertIn("adv_office", bootinfo)
		self.assertIsInstance(bootinfo.adv_office, dict)
		for key in ("company_name", "cnpj", "oab", "lawyer_name", "logo_url", "address"):
			self.assertIn(key, bootinfo.adv_office)

	def test_boot_session_handles_missing_settings(self):
		from advocacia.boot import boot_session

		bootinfo = frappe._dict()
		boot_session(bootinfo)
		self.assertIn("adv_office", bootinfo)
		self.assertTrue(bootinfo.adv_office["company_name"])
