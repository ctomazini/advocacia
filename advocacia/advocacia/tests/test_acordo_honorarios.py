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
			valor_total=10000,
			num_parcelas=2,
		)
		self.assertEqual(flt(acordo.valor_total_do_acordo), 10000)
		self.assertEqual(len(acordo.fee_installments), 2)

	def test_parcelas_soma_igual_total(self):
		acordo = create_test_acordo(valor_total=10000, num_parcelas=5)
		soma = sum(flt(p.valor_total) for p in acordo.fee_installments)
		self.assertAlmostEqual(soma, 10000, places=2)

	def test_parcelas_status_pendente(self):
		acordo = create_test_acordo(num_parcelas=3)
		self.assertTrue(all(p.status == "Pendente" for p in acordo.fee_installments))

	def test_sync_cria_pagamentos(self):
		acordo = create_test_acordo(num_parcelas=3, valor_total=9000)
		pagamentos = get_acordo_pagamentos(acordo.name)
		self.assertEqual(len(pagamentos), 3)

	def test_parcela_origem_id_vinculado(self):
		acordo = create_test_acordo(num_parcelas=2)
		for parcela in acordo.fee_installments:
			self.assertTrue(parcela.parcela_origem_id)
		pagamentos = get_acordo_pagamentos(acordo.name)
		origem_ids = {p.parcela_origem_id for p in pagamentos}
		parcela_ids = {p.parcela_origem_id for p in acordo.fee_installments}
		self.assertEqual(origem_ids, parcela_ids)

	def test_sem_servico_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Fee Agreement",
					"modo_honorarios": "Honorários Diretos",
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
					"modo_honorarios": "Honorários Diretos",
					"billing_type": "Valor fixo",
					"installment_count": 2,
					"data_primeira_parcela": today(),
					"fee_installments": [
						{
							"vencimento": today(),
							"valor_total": 100,
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
					"modo_honorarios": "Honorários Diretos",
					"billing_type": "Valor fixo",
					"valor_total_do_acordo": 10000,
					"fee_installments": [
						{
							"vencimento": today(),
							"valor_total": 1000,
							"valor_advogada": 0,
							"valor_cliente": 0,
							"status": "Pendente",
						}
					],
				}
			).insert(ignore_permissions=True)

	def test_acordo_quitado_quando_todos_pagamentos_recebidos(self):
		from advocacia.advocacia.tasks import on_pagamento_update

		acordo = create_test_acordo(num_parcelas=1, valor_total=1000)
		for pag in get_acordo_pagamentos(acordo.name):
			doc = frappe.get_doc("Legal Payment", pag.name)
			doc.status = "Recebido"
			doc.data_recebimento = today()
			doc.valor_recebido = doc.valor
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
				"modo_honorarios": "Acordo com Divisão",
				"billing_type": "Percentual do acordo",
				"percentual_advogada": 30,
				"percentual_cliente": 70,
				"valor_total_do_acordo": valor_acordo,
				"valor_advogada": valor_adv,
				"valor_cliente": valor_cli,
				"contingency_fee_amount": sucumbencia,
				"installment_count": 3,
				"data_primeira_parcela": today(),
				"fee_installments": [
					{
						"vencimento": today(),
						"valor_advogada": 3000,
						"valor_cliente": 7000,
						"contingency_amount": 3000,
						"valor_total": 13000,
						"status": "Pendente",
						"description": "Parcela 1 + Sucumbência",
					},
					{
						"vencimento": add_months(today(), 1),
						"valor_advogada": 3000,
						"valor_cliente": 7000,
						"contingency_amount": 0,
						"valor_total": 10000,
						"status": "Pendente",
						"description": "Parcela 2",
					},
					{
						"vencimento": add_months(today(), 2),
						"valor_advogada": 3000,
						"valor_cliente": 7000,
						"contingency_amount": 0,
						"valor_total": 10000,
						"status": "Pendente",
						"description": "Parcela 3",
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)
		soma = sum(flt(p.valor_total) for p in doc.fee_installments)
		self.assertAlmostEqual(soma, valor_acordo + sucumbencia, places=2)
		self.assertAlmostEqual(flt(doc.valor_advogada) + flt(doc.valor_cliente), valor_acordo, places=2)
