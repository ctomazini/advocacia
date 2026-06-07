"""Test Advocacia role-based permissions."""
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from advocacia.advocacia.painel_api import get_painel_data
from advocacia.advocacia.setup.permissions import setup_permissions
from advocacia.advocacia.setup.roles import create_roles
from advocacia.advocacia.tests.test_setup import create_test_acordo, create_test_legal_case, create_test_legal_task


def _create_user_with_role(role: str) -> str:
	email = f"perm_{role.replace(' ', '_').lower()}_{frappe.generate_hash(length=6)}@example.com"
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": "Perm",
			"last_name": role,
			"send_welcome_email": 0,
		}
	).insert(ignore_permissions=True)
	user.add_roles(role)
	frappe.clear_cache(user=user.name)
	return email


class TestAdvocaciaPermissions(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		create_roles()
		setup_permissions()
		frappe.clear_cache()

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_advocacia_roles_exist(self):
		self.assertTrue(frappe.db.exists("Role", "Advocacia User"))
		self.assertTrue(frappe.db.exists("Role", "Advocacia Manager"))

	def test_user_cannot_create_pagamento(self):
		user = _create_user_with_role("Advocacia User")
		servico = create_test_legal_case()
		frappe.set_user(user)
		doc = frappe.new_doc("Legal Payment")
		doc.update(
			{
				"legal_case": servico.name,
				"client": servico.client,
				"valor": 100,
				"data_vencimento": today(),
				"tipo_origem": "Honorários (Parcela)",
				"status": "Pendente",
			}
		)
		self.assertRaises(frappe.PermissionError, doc.insert)

	def test_manager_can_create_pagamento(self):
		user = _create_user_with_role("Advocacia Manager")
		servico = create_test_legal_case()
		acordo = create_test_acordo(servico=servico.name, num_parcelas=0, parcelas=[])
		frappe.set_user(user)
		doc = frappe.new_doc("Legal Payment")
		doc.update(
			{
				"legal_case": servico.name,
				"client": servico.client,
				"fee_agreement": acordo.name,
				"valor": 100,
				"data_vencimento": today(),
				"tipo_origem": "Honorários (Parcela)",
				"status": "Pendente",
			}
		)
		doc.insert()
		self.assertTrue(doc.name)

	def test_user_can_create_tarefa(self):
		user = _create_user_with_role("Advocacia User")
		frappe.set_user(user)
		doc = create_test_legal_task()
		self.assertTrue(doc.name)

	def test_painel_strips_financial_for_user(self):
		user = _create_user_with_role("Advocacia User")
		frappe.set_user(user)
		data = get_painel_data()
		self.assertNotIn("financeiro", data)
		self.assertNotIn("recebido_mes", data.get("kpis", {}))

	def test_painel_includes_financial_for_manager(self):
		user = _create_user_with_role("Advocacia Manager")
		frappe.set_user(user)
		data = get_painel_data()
		self.assertIn("financeiro", data)
		self.assertIn("recebido_mes", data.get("kpis", {}))
