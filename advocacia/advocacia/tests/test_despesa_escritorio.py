import frappe
from frappe.exceptions import MandatoryError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, getdate, today

from advocacia.advocacia.doctype.despesa_do_escritorio.despesa_do_escritorio import gerar_proxima_despesa
from advocacia.advocacia.tasks import verificar_despesas_vencidas
from advocacia.advocacia.tests.test_setup import create_test_despesa


class TestDespesaEscritorio(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_despesa_simples_pendente(self):
		desp = create_test_despesa(data_vencimento=add_days(today(), 30))
		self.assertEqual(desp.status, "Pendente")

	def test_vencimento_passado_marca_atrasado(self):
		desp = create_test_despesa(data_vencimento=add_days(today(), -3))
		desp.reload()
		self.assertEqual(desp.status, "Atrasado")

	def test_data_pagamento_marca_pago(self):
		desp = create_test_despesa()
		desp.data_pagamento = today()
		desp.save(ignore_permissions=True)
		desp.reload()
		self.assertEqual(desp.status, "Pago")

	def test_recorrente_mensal_proximo_vencimento(self):
		venc = getdate("2026-06-01")
		desp = create_test_despesa(data_vencimento=venc, recorrente=1, frequencia="Mensal")
		self.assertEqual(getdate(desp.proximo_vencimento), getdate("2026-07-01"))

	def test_recorrente_trimestral(self):
		venc = getdate("2026-06-01")
		desp = create_test_despesa(data_vencimento=venc, recorrente=1, frequencia="Trimestral")
		self.assertEqual(getdate(desp.proximo_vencimento), getdate("2026-09-01"))

	def test_scheduler_marca_atrasado(self):
		desp = create_test_despesa(data_vencimento=add_days(today(), -2))
		frappe.db.set_value("Despesa do Escritorio", desp.name, "status", "Pendente")
		verificar_despesas_vencidas()
		self.assertEqual(
			frappe.db.get_value("Despesa do Escritorio", desp.name, "status"), "Atrasado"
		)

	def test_despesa_paga_nao_alterada_scheduler(self):
		desp = create_test_despesa(data_vencimento=add_days(today(), -2))
		frappe.db.set_value("Despesa do Escritorio", desp.name, "status", "Pago")
		verificar_despesas_vencidas()
		self.assertEqual(
			frappe.db.get_value("Despesa do Escritorio", desp.name, "status"), "Pago"
		)

	def test_gerar_proxima_despesa(self):
		venc = getdate("2026-06-01")
		desp = create_test_despesa(data_vencimento=venc, recorrente=1, frequencia="Mensal")
		nova_name = gerar_proxima_despesa(desp.name)
		nova = frappe.get_doc("Despesa do Escritorio", nova_name)
		self.assertEqual(getdate(nova.data_vencimento), getdate("2026-07-01"))
		self.assertEqual(nova.status, "Pendente")

	def test_gerar_proxima_nao_recorrente_falha(self):
		desp = create_test_despesa(recorrente=0)
		with self.assertRaises(ValidationError):
			gerar_proxima_despesa(desp.name)

	def test_sem_descricao_falha(self):
		with self.assertRaises(MandatoryError):
			frappe.get_doc(
				{
					"doctype": "Despesa do Escritorio",
					"categoria": "Aluguel",
					"valor": 100,
				}
			).insert(ignore_permissions=True)

	def test_categorias_validas(self):
		for cat in ["Aluguel", "Energia", "Outros"]:
			desp = create_test_despesa(categoria=cat)
			self.assertEqual(desp.categoria, cat)
