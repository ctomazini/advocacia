import frappe
from frappe.tests.utils import FrappeTestCase


DOCTYPES_WITH_CONNECTIONS = (
	"Legal Case",
	"Legal Payment",
	"Fee Agreement",
	"Client",
	"Deadline",
	"Hearing",
	"Legal Task",
	"Time Entry",
	"Service Record",
)


class TestDocTypeDashboard(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_connection_shortcuts_not_duplicated(self):
		for doctype in DOCTYPES_WITH_CONNECTIONS:
			data = frappe.get_meta(doctype).get_dashboard_data()
			transactions = data.transactions or []
			if not transactions:
				self.assertTrue(
					data.internal_links,
					f"{doctype}: dashboard sem transactions nem internal_links",
				)
				continue
			seen_items: list[str] = []
			for group in transactions:
				self.assertTrue(
					group.get("label"),
					f"{doctype}: grupo de conexões sem label ({group})",
				)
				for item in group.get("items") or []:
					self.assertNotIn(
						item,
						seen_items,
						f"{doctype}: atalho duplicado para {item}",
					)
					seen_items.append(item)

	def test_get_dashboard_data_does_not_raise(self):
		for doctype in DOCTYPES_WITH_CONNECTIONS:
			data = frappe.get_meta(doctype).get_dashboard_data()
			self.assertIn("transactions", data)
