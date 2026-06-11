import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_months, flt, today

from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_legal_case,
	get_acordo_pagamentos,
)


class TestAcordoHonorarios(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_honorarios_diretos_valor_fixo(self):
		acordo = create_test_acordo(
			modo="Honorários Diretos",
			tipo_cobranca="Valor fixo",
			total_amount=10000,
			num_parcelas=2,
		)
		self.assertEqual(flt(acordo.total_agreement_value), 10000)
		self.assertEqual(len(acordo.fee_installments), 2)

	def test_parcelas_soma_igual_total(self):
		acordo = create_test_acordo(total_amount=10000, num_parcelas=5)
		soma = sum(flt(p.total_amount) for p in acordo.fee_installments)
		self.assertAlmostEqual(soma, 10000, places=2)

	def test_parcelas_status_pendente(self):
		acordo = create_test_acordo(num_parcelas=3)
		self.assertTrue(all(p.status == "Pendente" for p in acordo.fee_installments))

	def test_sync_cria_pagamentos(self):
		acordo = create_test_acordo(num_parcelas=3, total_amount=9000)
		pagamentos = get_acordo_pagamentos(acordo.name)
		self.assertEqual(len(pagamentos), 3)

	def test_parcela_origem_id_vinculado(self):
		acordo = create_test_acordo(num_parcelas=2)
		for parcela in acordo.fee_installments:
			self.assertTrue(parcela.installment_origin_id)
		pagamentos = get_acordo_pagamentos(acordo.name)
		origem_ids = {p.installment_origin_id for p in pagamentos}
		parcela_ids = {p.installment_origin_id for p in acordo.fee_installments}
		self.assertEqual(origem_ids, parcela_ids)

	def test_sem_servico_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Fee Agreement",
					"fee_mode": "Honorários Diretos",
					"billing_type": "Valor fixo",
				}
			).insert(ignore_permissions=True)

	def test_parcelas_sem_valor_total_falha(self):
		servico = create_test_legal_case().name
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Fee Agreement",
					"legal_case": servico,
					"fee_mode": "Honorários Diretos",
					"billing_type": "Valor fixo",
					"installment_count": 2,
					"first_installment_date": today(),
					"fee_installments": [
						{
							"due_date": today(),
							"total_amount": 100,
							"status": "Pendente",
						}
					],
				}
			).insert(ignore_permissions=True)

	def test_soma_parcelas_diferente_total_falha(self):
		servico = create_test_legal_case().name
		cliente = frappe.db.get_value("Legal Case", servico, "client")
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Fee Agreement",
					"legal_case": servico,
					"client": cliente,
					"fee_mode": "Honorários Diretos",
					"billing_type": "Valor fixo",
					"total_agreement_value": 10000,
					"fee_installments": [
						{
							"due_date": today(),
							"total_amount": 1000,
							"lawyer_amount": 0,
							"client_amount": 0,
							"status": "Pendente",
						}
					],
				}
			).insert(ignore_permissions=True)

	def test_acordo_quitado_quando_todos_pagamentos_recebidos(self):
		from advocacia.advocacia.tasks import on_pagamento_update

		acordo = create_test_acordo(num_parcelas=1, total_amount=1000)
		for pag in get_acordo_pagamentos(acordo.name):
			doc = frappe.get_doc("Legal Payment", pag.name)
			doc.status = "Recebido"
			doc.received_date = today()
			doc.received_amount = doc.amount
			doc.save(ignore_permissions=True)
			on_pagamento_update(doc, "on_update")

		status = frappe.db.get_value("Fee Agreement", acordo.name, "status")
		self.assertEqual(status, "Quitado")

	def test_acordo_divisao_com_sucumbencia_soma_parcelas(self):
		"""Acordo 30k + 10% sucumbência: parcelas somam 33k, base adv+cli = 30k."""
		servico = create_test_legal_case().name
		cliente = frappe.db.get_value("Legal Case", servico, "client")
		valor_acordo = 30000
		valor_adv = 9000
		valor_cli = 21000
		sucumbencia = 3000
		doc = frappe.get_doc(
			{
				"doctype": "Fee Agreement",
				"legal_case": servico,
				"client": cliente,
				"fee_mode": "Divisão advogada/cliente",
				"billing_type": "Percentual do acordo",
				"lawyer_percentage": 30,
				"client_percentage": 70,
				"total_agreement_value": valor_acordo,
				"lawyer_amount": valor_adv,
				"client_amount": valor_cli,
				"contingency_fee_amount": sucumbencia,
				"installment_count": 3,
				"first_installment_date": today(),
				"fee_installments": [
					{
						"due_date": today(),
						"lawyer_amount": 3000,
						"client_amount": 7000,
						"contingency_amount": 3000,
						"total_amount": 13000,
						"status": "Pendente",
						"description": "Parcela 1 + Sucumbência",
					},
					{
						"due_date": add_months(today(), 1),
						"lawyer_amount": 3000,
						"client_amount": 7000,
						"contingency_amount": 0,
						"total_amount": 10000,
						"status": "Pendente",
						"description": "Parcela 2",
					},
					{
						"due_date": add_months(today(), 2),
						"lawyer_amount": 3000,
						"client_amount": 7000,
						"contingency_amount": 0,
						"total_amount": 10000,
						"status": "Pendente",
						"description": "Parcela 3",
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)
		soma = sum(flt(p.total_amount) for p in doc.fee_installments)
		self.assertAlmostEqual(soma, valor_acordo + sucumbencia, places=2)
		self.assertAlmostEqual(flt(doc.lawyer_amount) + flt(doc.client_amount), valor_acordo, places=2)
