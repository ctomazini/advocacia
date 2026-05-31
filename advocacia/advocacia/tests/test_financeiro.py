import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from advocacia.advocacia.financeiro import (
	bulk_delete_pagamentos,
	resync_pagamentos_acordo,
	sincronizar_pagamentos_do_acordo,
)
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_registro_atos,
	get_acordo_pagamentos,
)


class TestFinanceiro(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_sincronizar_cria_pagamentos(self):
		acordo = create_test_acordo(num_parcelas=3, valor_total=3000)
		result = sincronizar_pagamentos_do_acordo(acordo.name)
		self.assertGreaterEqual(result.get("criados", 0) + len(get_acordo_pagamentos(acordo.name)), 3)

	def test_resync_atualiza_valor_parcela(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=1000)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		acordo_doc = frappe.get_doc("Acordo de Honorarios Processuais", acordo.name)
		acordo_doc.table_ztjx[0].valor_total = 1500
		acordo_doc.valor_total_do_acordo = 1500
		acordo_doc.save(ignore_permissions=True)
		resync_pagamentos_acordo(acordo.name)
		self.assertEqual(flt(frappe.db.get_value("Pagamento", pag_name, "valor")), 1500)

	def test_acordo_sem_parcelas_sem_pagamento(self):
		acordo = create_test_acordo(num_parcelas=0, valor_total=0, parcelas=[])
		acordo.número_de_parcelas = 0
		acordo.save(ignore_permissions=True)
		pags = get_acordo_pagamentos(acordo.name)
		self.assertEqual(len(pags), 0)

	def test_gerar_pagamento_atos_soma_valores(self):
		registro = create_test_registro_atos()
		from advocacia.advocacia.financeiro import gerar_pagamento_atos

		result = gerar_pagamento_atos(registro.name)
		pag = frappe.get_doc("Pagamento", result["pagamento"])
		self.assertEqual(flt(pag.valor), 4500)

	def test_bulk_delete_pagamentos_pendentes(self):
		acordo = create_test_acordo(num_parcelas=2, valor_total=2000)
		names = [p.name for p in get_acordo_pagamentos(acordo.name)]
		result = bulk_delete_pagamentos(names)
		self.assertEqual(len(result["excluidos"]), 2)

	def test_bulk_delete_ignora_recebido(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=500)
		pag = frappe.get_doc("Pagamento", get_acordo_pagamentos(acordo.name)[0].name)
		pag.status = "Recebido"
		pag.data_recebimento = today()
		pag.valor_recebido = pag.valor
		pag.save(ignore_permissions=True)
		result = bulk_delete_pagamentos([pag.name])
		self.assertEqual(len(result["ignorados"]), 1)

	def test_cancelar_cobranca_atos(self):
		registro = create_test_registro_atos()
		from advocacia.advocacia.financeiro import (
			cancelar_cobranca_pagamento_atos,
			gerar_pagamento_atos,
		)

		result = gerar_pagamento_atos(registro.name)
		cancelar_cobranca_pagamento_atos(result["pagamento"])
		pag = frappe.get_doc("Pagamento", result["pagamento"])
		self.assertEqual(pag.status, "Cancelado")
