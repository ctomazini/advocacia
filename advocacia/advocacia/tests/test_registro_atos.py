import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

from advocacia.advocacia.financeiro import (
	cancelar_cobranca_pagamento_atos,
	gerar_pagamento_atos,
)
from advocacia.advocacia.tests.test_setup import create_test_registro_atos, create_test_servico


class TestRegistroAtos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_totais_calculados(self):
		registro = create_test_registro_atos()
		self.assertEqual(flt(registro.total_geral), 4500)
		self.assertEqual(flt(registro.total_pendente), 4500)
		self.assertEqual(flt(registro.total_cobrado), 0)

	def test_gerar_cobranca_cria_pagamento(self):
		registro = create_test_registro_atos()
		result = gerar_pagamento_atos(registro.name)
		pagamento_name = result.get("pagamento")
		self.assertTrue(pagamento_name)
		pag = frappe.get_doc("Pagamento", pagamento_name)
		self.assertEqual(pag.tipo_origem, "Atos Advocatícios")
		self.assertEqual(flt(pag.valor), 4500)

	def test_atos_marcados_cobrado(self):
		registro = create_test_registro_atos()
		gerar_pagamento_atos(registro.name)
		registro.reload()
		self.assertTrue(all(a.status == "Cobrado" for a in registro.atos))
		self.assertEqual(registro.status, "Cobrado")

	def test_cobranca_parcial(self):
		registro = create_test_registro_atos(
			atos=[
				{
					"data": today(),
					"tipo": "Inicial",
					"valor": 1000,
					"descricao": "A",
					"status": "Cobrado",
				},
				{
					"data": today(),
					"tipo": "Defesa",
					"valor": 2000,
					"descricao": "B",
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
		cancelar_cobranca_pagamento_atos(result["pagamento"])
		registro.reload()
		self.assertTrue(all(a.status == "Pendente" for a in registro.atos))

	def test_cliente_preenchido_via_servico(self):
		servico = create_test_servico()
		registro = create_test_registro_atos(servico=servico.name)
		self.assertEqual(registro.cliente, servico.cliente)

	def test_ato_sem_data_falha(self):
		servico = create_test_servico().name
		with self.assertRaises((ValidationError, frappe.exceptions.MandatoryError)):
			frappe.get_doc(
				{
					"doctype": "Registro de Atos",
					"servico": servico,
					"atos": [{"tipo": "Inicial", "valor": 100}],
				}
			).insert(ignore_permissions=True)
