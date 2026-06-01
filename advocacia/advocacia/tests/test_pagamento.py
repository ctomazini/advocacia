import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from advocacia.advocacia.financeiro import TIPO_ATOS, TIPO_HONORARIOS
from advocacia.advocacia.tasks import verificar_parcelas_vencidas
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_pagamento,
	create_test_registro_atos,
	get_acordo_pagamentos,
)


class TestPagamento(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_pendente_para_recebido(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag = frappe.get_doc("Pagamento", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Recebido"
		pag.data_recebimento = today()
		pag.valor_recebido = pag.valor
		pag.save(ignore_permissions=True)
		self.assertEqual(pag.status, "Recebido")

	def test_scheduler_marca_vencido(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		frappe.db.set_value(
			"Pagamento",
			pag_name,
			{"data_vencimento": add_days(today(), -5), "status": "Pendente"},
		)
		verificar_parcelas_vencidas()
		self.assertEqual(frappe.db.get_value("Pagamento", pag_name, "status"), "Vencido")

	def test_cancelado_imutavel(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag = frappe.get_doc("Pagamento", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Cancelado"
		pag.save(ignore_permissions=True)
		pag.reload()
		with self.assertRaises(ValidationError):
			pag.status = "Pendente"
			pag.save(ignore_permissions=True)

	def test_honorarios_exige_acordo(self):
		servico = create_test_acordo(num_parcelas=0, valor_total=0).servico
		cliente = frappe.db.get_value("Servico", servico, "cliente")
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Pagamento",
					"servico": servico,
					"cliente": cliente,
					"valor": 100,
					"data_vencimento": today(),
					"status": "Pendente",
					"tipo_origem": TIPO_HONORARIOS,
				}
			).insert(ignore_permissions=True)

	def test_atos_exige_registro(self):
		servico = create_test_acordo(num_parcelas=0, valor_total=0).servico
		cliente = frappe.db.get_value("Servico", servico, "cliente")
		with self.assertRaises(ValidationError):
			frappe.get_doc(
				{
					"doctype": "Pagamento",
					"servico": servico,
					"cliente": cliente,
					"valor": 100,
					"data_vencimento": today(),
					"status": "Pendente",
					"tipo_origem": TIPO_ATOS,
				}
			).insert(ignore_permissions=True)

	def test_receber_atualiza_parcela(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=800)
		pag = frappe.get_doc("Pagamento", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Recebido"
		pag.data_recebimento = today()
		pag.valor_recebido = pag.valor
		pag.save(ignore_permissions=True)
		parcela = frappe.get_all(
			"Parcela de Honorarios",
			filters={"parent": acordo.name},
			fields=["status"],
		)[0]
		self.assertEqual(parcela.status, "Recebido")

	def test_valor_negativo_falha(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=100)
		pag = frappe.get_doc("Pagamento", get_acordo_pagamentos(acordo.name)[0].name)
		with self.assertRaises(ValidationError):
			pag.valor = -1
			pag.save(ignore_permissions=True)

	def test_trash_pagamento_recebido_bloqueado(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=100)
		pag = frappe.get_doc("Pagamento", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Recebido"
		pag.data_recebimento = today()
		pag.valor_recebido = pag.valor
		pag.save(ignore_permissions=True)
		with self.assertRaises(ValidationError):
			pag.delete(ignore_permissions=True)

	def test_pagamento_atos_via_registro(self):
		registro = create_test_registro_atos()
		from advocacia.advocacia.financeiro import gerar_pagamento_atos

		result = gerar_pagamento_atos(registro.name)
		self.assertTrue(result.get("pagamento"))
		self.assertTrue(frappe.db.exists("Pagamento", result["pagamento"]))
