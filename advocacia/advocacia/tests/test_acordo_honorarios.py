import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_months, flt, today

from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_servico,
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
		self.assertEqual(len(acordo.table_ztjx), 2)

	def test_parcelas_soma_igual_total(self):
		acordo = create_test_acordo(valor_total=10000, num_parcelas=5)
		soma = sum(flt(p.valor_total) for p in acordo.table_ztjx)
		self.assertAlmostEqual(soma, 10000, places=2)

	def test_parcelas_status_pendente(self):
		acordo = create_test_acordo(num_parcelas=3)
		self.assertTrue(all(p.status == "Pendente" for p in acordo.table_ztjx))

	def test_sync_cria_pagamentos(self):
		acordo = create_test_acordo(num_parcelas=3, valor_total=9000)
		pagamentos = get_acordo_pagamentos(acordo.name)
		self.assertEqual(len(pagamentos), 3)

	def test_parcela_origem_id_vinculado(self):
		acordo = create_test_acordo(num_parcelas=2)
		for parcela in acordo.table_ztjx:
			self.assertTrue(parcela.parcela_origem_id)
		pagamentos = get_acordo_pagamentos(acordo.name)
		origem_ids = {p.parcela_origem_id for p in pagamentos}
		parcela_ids = {p.parcela_origem_id for p in acordo.table_ztjx}
		self.assertEqual(origem_ids, parcela_ids)

	def test_sem_servico_falha(self):
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Acordo de Honorarios Processuais",
					"modo_honorarios": "Honorários Diretos",
					"tipo_de_cobrança": "Valor fixo",
				}
			).insert(ignore_permissions=True)

	def test_parcelas_sem_valor_total_falha(self):
		servico = create_test_servico().name
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Acordo de Honorarios Processuais",
					"servico": servico,
					"modo_honorarios": "Honorários Diretos",
					"tipo_de_cobrança": "Valor fixo",
					"número_de_parcelas": 2,
					"data_primeira_parcela": today(),
					"table_ztjx": [
						{
							"vencimento": today(),
							"valor_total": 100,
							"status": "Pendente",
						}
					],
				}
			).insert(ignore_permissions=True)

	def test_soma_parcelas_diferente_total_falha(self):
		servico = create_test_servico().name
		cliente = frappe.db.get_value("Servico", servico, "cliente")
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Acordo de Honorarios Processuais",
					"servico": servico,
					"cliente": cliente,
					"modo_honorarios": "Honorários Diretos",
					"tipo_de_cobrança": "Valor fixo",
					"valor_total_do_acordo": 10000,
					"table_ztjx": [
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
			doc = frappe.get_doc("Pagamento", pag.name)
			doc.status = "Recebido"
			doc.data_recebimento = today()
			doc.valor_recebido = doc.valor
			doc.save(ignore_permissions=True)
			on_pagamento_update(doc, "on_update")

		status = frappe.db.get_value("Acordo de Honorarios Processuais", acordo.name, "status")
		self.assertEqual(status, "Quitado")
