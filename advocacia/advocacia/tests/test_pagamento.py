import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from advocacia.advocacia.financeiro import TIPO_ATOS, TIPO_HONORARIOS
from advocacia.advocacia.tasks import verificar_parcelas_vencidas
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_legal_payment,
	create_test_registro_atos,
	get_acordo_pagamentos,
)


class TestLegalPayment(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_pendente_para_recebido(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag = frappe.get_doc("Legal Payment", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Recebido"
		pag.received_date = today()
		pag.received_amount = pag.amount
		pag.save(ignore_permissions=True)
		self.assertEqual(pag.status, "Recebido")

	def test_titulo_composto(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag = frappe.get_doc("Legal Payment", get_acordo_pagamentos(acordo.name)[0].name)
		cliente_nome = frappe.db.get_value("Client", pag.client, "client_name")
		self.assertIn(pag.name, pag.title)
		self.assertIn(cliente_nome, pag.title)

	def test_scheduler_marca_vencido(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		frappe.db.set_value(
			"Legal Payment",
			pag_name,
			{"due_date": add_days(today(), -5), "status": "Pendente"},
		)
		verificar_parcelas_vencidas()
		self.assertEqual(frappe.db.get_value("Legal Payment", pag_name, "status"), "Vencido")

	def test_sync_acordo_marca_vencido_por_data(self):
		from advocacia.advocacia.financeiro import sincronizar_pagamentos_do_acordo

		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		parcela_name = frappe.get_all(
			"Fee Installment",
			filters={"parent": acordo.name},
			pluck="name",
		)[0]
		past = add_days(today(), -5)
		frappe.db.set_value(
			"Legal Payment",
			pag_name,
			{"due_date": past, "status": "Pendente"},
		)
		frappe.db.set_value(
			"Fee Installment",
			parcela_name,
			{"due_date": past, "status": "Pendente"},
		)

		doc = frappe.get_doc("Fee Agreement", acordo.name)
		sincronizar_pagamentos_do_acordo(doc)

		self.assertEqual(frappe.db.get_value("Legal Payment", pag_name, "status"), "Vencido")

	def test_sync_acordo_nao_reverte_vencido(self):
		from advocacia.advocacia.financeiro import sincronizar_pagamentos_do_acordo

		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		parcela_name = frappe.get_all(
			"Fee Installment",
			filters={"parent": acordo.name},
			pluck="name",
		)[0]
		past = add_days(today(), -5)
		frappe.db.set_value(
			"Legal Payment",
			pag_name,
			{"due_date": past, "status": "Vencido"},
		)
		frappe.db.set_value(
			"Fee Installment",
			parcela_name,
			{"due_date": past, "status": "Pendente"},
		)

		doc = frappe.get_doc("Fee Agreement", acordo.name)
		sincronizar_pagamentos_do_acordo(doc)

		self.assertEqual(frappe.db.get_value("Legal Payment", pag_name, "status"), "Vencido")

	def test_cancelado_imutavel(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=500)
		pag = frappe.get_doc("Legal Payment", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Cancelado"
		pag.save(ignore_permissions=True)
		pag.reload()
		with self.assertRaises(ValidationError):
			pag.status = "Pendente"
			pag.save(ignore_permissions=True)

	def test_honorarios_exige_acordo(self):
		servico = create_test_acordo(num_parcelas=0, total_amount=0).legal_case
		cliente = frappe.db.get_value("Legal Case", servico, "client")
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Legal Payment",
					"legal_case": servico,
					"client": cliente,
					"amount": 100,
					"due_date": today(),
					"status": "Pendente",
					"origin_type": TIPO_HONORARIOS,
				}
			).insert(ignore_permissions=True)

	def test_atos_exige_registro(self):
		servico = create_test_acordo(num_parcelas=0, total_amount=0).legal_case
		cliente = frappe.db.get_value("Legal Case", servico, "client")
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Legal Payment",
					"legal_case": servico,
					"client": cliente,
					"amount": 100,
					"due_date": today(),
					"status": "Pendente",
					"origin_type": TIPO_ATOS,
				}
			).insert(ignore_permissions=True)

	def test_receber_atualiza_parcela(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=800)
		pag = frappe.get_doc("Legal Payment", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Recebido"
		pag.received_date = today()
		pag.received_amount = pag.amount
		pag.save(ignore_permissions=True)
		parcela = frappe.get_all(
			"Fee Installment",
			filters={"parent": acordo.name},
			fields=["status"],
		)[0]
		self.assertEqual(parcela.status, "Recebido")

	def test_valor_negativo_falha(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=100)
		pag = frappe.get_doc("Legal Payment", get_acordo_pagamentos(acordo.name)[0].name)
		with self.assertRaises(ValidationError):
			pag.amount = -1
			pag.save(ignore_permissions=True)

	def test_trash_pagamento_recebido_bloqueado(self):
		acordo = create_test_acordo(num_parcelas=1, total_amount=100)
		pag = frappe.get_doc("Legal Payment", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Recebido"
		pag.received_date = today()
		pag.received_amount = pag.amount
		pag.save(ignore_permissions=True)
		with self.assertRaises(ValidationError):
			pag.delete(ignore_permissions=True)

	def test_legal_payment_atos_via_registro(self):
		registro = create_test_registro_atos()
		from advocacia.advocacia.financeiro import gerar_pagamento_atos

		result = gerar_pagamento_atos(registro.name)
		self.assertTrue(result.get("payment"))
		self.assertTrue(frappe.db.exists("Legal Payment", result["payment"]))
