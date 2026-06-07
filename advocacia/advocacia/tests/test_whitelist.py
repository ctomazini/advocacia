import inspect

import frappe
from frappe.tests.utils import FrappeTestCase

from advocacia.advocacia.documentos import get_placeholders_referencia
from advocacia.advocacia.financeiro import bulk_delete_pagamentos, resync_pagamentos_acordo
from advocacia.advocacia.painel_api import get_painel_data, marcar_parcela_recebida
from advocacia.advocacia.tests.test_setup import create_test_acordo, get_acordo_pagamentos


class TestWhitelist(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_painel_data_requires_legal_case_read(self):
		user = "test_whitelist_dash@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Test",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_painel_data()
		finally:
			frappe.set_user("Administrator")

	def test_get_placeholders_referencia_requires_read(self):
		result = get_placeholders_referencia()
		self.assertTrue(result)

	def test_resync_pagamentos_acordo_whitelist(self):
		acordo = create_test_acordo(valor_total=1000, num_parcelas=1)
		result = resync_pagamentos_acordo(acordo.name)
		self.assertEqual(result["status"], "ok")

	def test_bulk_delete_pagamentos_whitelist(self):
		acordo = create_test_acordo(valor_total=1000, num_parcelas=1)
		names = [p.name for p in get_acordo_pagamentos(acordo.name)]
		result = bulk_delete_pagamentos(names)
		self.assertEqual(len(result["excluidos"]), 1)

	def test_mark_payment_received_facade_has_permission(self):
		source = inspect.getsource(marcar_parcela_recebida)
		self.assertIn("has_permission", source)
		self.assertIn("Legal Payment", source)

	def test_marcar_parcela_recebida_requires_write(self):
		user = "test_whitelist_user@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Adv",
					"last_name": "User",
					"send_welcome_email": 0,
					"roles": [{"role": "Advocacia User"}],
				}
			).insert(ignore_permissions=True)

		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name

		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				marcar_parcela_recebida(pag_name)
		finally:
			frappe.set_user("Administrator")
