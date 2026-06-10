import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from advocacia.advocacia.financeiro import (
	cancelar_cobranca_pagamento_atos,
	gerar_pagamento_atos,
)
from advocacia.advocacia.tests.test_setup import create_test_registro_atos, create_test_legal_case


class TestRegistroAtos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_totais_calculados(self):
		registro = create_test_registro_atos()
		self.assertEqual(flt(registro.grand_total), 4500)
		self.assertEqual(flt(registro.pending_total), 4500)
		self.assertEqual(flt(registro.billed_total), 0)

	def test_gerar_cobranca_cria_pagamento(self):
		registro = create_test_registro_atos()
		result = gerar_pagamento_atos(registro.name)
		pagamento_name = result.get("payment")
		self.assertTrue(pagamento_name)
		pag = frappe.get_doc("Legal Payment", pagamento_name)
		self.assertEqual(pag.origin_type, "Atos Advocatícios")
		self.assertEqual(flt(pag.amount), 4500)

	def test_atos_marcados_cobrado(self):
		registro = create_test_registro_atos()
		result = gerar_pagamento_atos(registro.name)
		registro.reload()
		self.assertTrue(all(a.status == "Cobrado" for a in registro.acts))
		self.assertTrue(all(a.payment == result["payment"] for a in registro.acts))
		self.assertEqual(registro.status, "Cobrado")

	def test_cobranca_parcial(self):
		registro = create_test_registro_atos(
			atos=[
				{
					"act_date": today(),
					"type": "Inicial",
					"amount": 1000,
					"description": "A",
					"status": "Cobrado",
				},
				{
					"act_date": today(),
					"type": "Defesa",
					"amount": 2000,
					"description": "B",
					"status": "Pendente",
				},
			]
		)
		registro.reload()
		self.assertEqual(registro.status, "Parcialmente cobrado")

	def test_sem_atos_pendentes_falha_cobranca(self):
		registro = create_test_registro_atos(atos=[])
		with self.assertRaises(ValidationError):
			gerar_pagamento_atos(registro.name)

	def test_cancelar_cobranca_libera_atos(self):
		registro = create_test_registro_atos()
		result = gerar_pagamento_atos(registro.name)
		cancelar_cobranca_pagamento_atos(result["payment"])
		registro.reload()
		self.assertTrue(all(a.status == "Pendente" for a in registro.acts))

	def test_client_preenchido_via_servico(self):
		servico = create_test_legal_case()
		registro = create_test_registro_atos(servico=servico.name)
		self.assertEqual(registro.client, servico.client)

	def test_ato_sem_data_falha(self):
		servico = create_test_legal_case().name
		with self.assertRaises((ValidationError, frappe.exceptions.MandatoryError)):
			frappe.get_doc(
				{
					"doctype": "Service Record",
					"legal_case": servico,
					"acts": [{"type": "Inicial", "amount": 100}],
				}
			).insert(ignore_permissions=True)
