import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from advocacia.advocacia.report.fluxo_de_caixa.fluxo_de_caixa import execute as fluxo_execute
from advocacia.advocacia.tests.test_setup import create_test_court_cost, create_test_legal_case


class TestCourtCost(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_crud_valido(self):
		custa = create_test_court_cost()
		self.assertTrue(custa.name)
		self.assertEqual(custa.status, "Pendente")

	def test_client_via_servico(self):
		servico = create_test_legal_case()
		cliente = frappe.db.get_value("Legal Case", servico.name, "client")
		custa = create_test_court_cost(servico=servico.name)
		self.assertEqual(custa.client, cliente)

	def test_status_pendente_para_pago(self):
		custa = create_test_court_cost()
		custa.data_pagamento = today()
		custa.save(ignore_permissions=True)
		custa.reload()
		self.assertEqual(custa.status, "Pago")

	def test_status_pago_para_repassado(self):
		custa = create_test_court_cost(data_pagamento=today(), status="Pago")
		custa.data_repasse = today()
		custa.save(ignore_permissions=True)
		custa.reload()
		self.assertEqual(custa.status, "Repassado")

	def test_cancelado_nao_pode_alterar(self):
		custa = create_test_court_cost(status="Cancelado")
		custa.valor = 999
		with self.assertRaises(ValidationError):
			custa.save(ignore_permissions=True)

	def test_sem_servico_falha(self):
		from frappe.exceptions import ValidationError

		with self.assertRaises((MandatoryError, ValidationError)):
			frappe.get_doc(
				{
					"doctype": "Court Cost",
					"descricao": "Teste",
					"tipo": "Taxa Judicial",
					"valor": 100,
				}
			).insert(ignore_permissions=True)

	def test_integracao_fluxo_de_caixa(self):
		custa = create_test_court_cost(
			valor=750,
			data_pagamento=today(),
			status="Pago",
		)
		columns, data, _msg, _chart, _summary = fluxo_execute({"meses": 1})
		saidas = [r for r in data if r.get("origem") == "Court Cost"]
		self.assertTrue(any(r.get("documento") == custa.name for r in saidas))
