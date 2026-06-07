"""Test seed-demo creates and clears demo data correctly."""

import frappe
from frappe.tests import IntegrationTestCase

from advocacia.advocacia.setup.seed_demo import (
	DEMO_MARKER,
	clear_demo_data,
	seed_demo_data,
)


class TestSeedDemo(IntegrationTestCase):
	def setUp(self):
		clear_demo_data()

	def tearDown(self):
		frappe.db.rollback()

	def test_seed_creates_documents(self):
		count = seed_demo_data()
		self.assertGreater(count, 0)
		clientes = frappe.get_all(
			"Client",
			filters={"nome": ["like", f"%{DEMO_MARKER}%"]},
		)
		self.assertGreater(len(clientes), 0)

	def test_seed_is_idempotent(self):
		count1 = seed_demo_data()
		frappe.db.commit()
		count2 = seed_demo_data()
		self.assertEqual(count1, count2)

	def test_clear_removes_all_demo(self):
		seed_demo_data()
		frappe.db.commit()
		removed = clear_demo_data()
		frappe.db.commit()
		self.assertGreater(removed, 0)
		remaining = frappe.db.count("Client", {"nome": ["like", f"%{DEMO_MARKER}%"]})
		self.assertEqual(remaining, 0)

	def test_guard_blocks_production(self):
		from advocacia.advocacia.setup.seed_demo import _guard_production

		_guard_production()
