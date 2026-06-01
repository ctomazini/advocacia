"""Testes do padrão homogêneo de títulos (Filosofia A)."""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, get_datetime, today

from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_audiencia,
	create_test_cliente,
	create_test_pagamento,
	create_test_registro_atos,
	create_test_servico,
	get_acordo_pagamentos,
)


class TestTitulosDistintivos(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_registro_atos_titulo_distintivo_por_data(self):
		cliente = create_test_cliente()
		servico = create_test_servico(cliente=cliente.name)
		a1 = frappe.get_doc(
			{
				"doctype": "Registro de Atos",
				"servico": servico.name,
				"data_abertura": "2026-03-15",
				"atos": [{"data": "2026-03-15", "tipo": "Inicial", "valor": 100}],
			}
		).insert(ignore_permissions=True)
		a2 = frappe.get_doc(
			{
				"doctype": "Registro de Atos",
				"servico": servico.name,
				"data_abertura": "2026-03-20",
				"atos": [{"data": "2026-03-20", "tipo": "Inicial", "valor": 200}],
			}
		).insert(ignore_permissions=True)
		self.assertNotEqual(a1.title, a2.title)
		self.assertIn(cliente.nome, a1.title)
		self.assertIn(cliente.nome, a2.title)

	def test_registro_atos_titulo_manual_preservado(self):
		registro = create_test_registro_atos()
		registro.title = "Meu título custom"
		registro.save(ignore_permissions=True)
		registro.reload()
		self.assertEqual(registro.title, "Meu título custom")

	def test_audiencia_titulo_distintivo_por_data(self):
		servico = create_test_servico()
		a1 = create_test_audiencia(
			servico=servico.name,
			data_hora=get_datetime("2026-03-15 10:00:00"),
		)
		a2 = create_test_audiencia(
			servico=servico.name,
			data_hora=get_datetime("2026-03-20 14:00:00"),
		)
		self.assertNotEqual(a1.title, a2.title)

	def test_audiencia_titulo_manual_preservado(self):
		aud = create_test_audiencia()
		aud.title = "Meu título custom"
		aud.save(ignore_permissions=True)
		aud.reload()
		self.assertEqual(aud.title, "Meu título custom")

	def test_pagamento_titulo_distintivo_por_data(self):
		acordo = create_test_acordo(num_parcelas=2, valor_total=1000)
		pagamentos = get_acordo_pagamentos(acordo.name)
		self.assertGreaterEqual(len(pagamentos), 2)
		p1 = frappe.get_doc("Pagamento", pagamentos[0].name)
		p2 = frappe.get_doc("Pagamento", pagamentos[1].name)
		self.assertNotEqual(p1.data_vencimento, p2.data_vencimento)
		self.assertNotEqual(p1.title, p2.title)

	def test_pagamento_titulo_manual_preservado(self):
		pag = create_test_pagamento()
		pag.title = "Meu título custom"
		pag.save(ignore_permissions=True)
		pag.reload()
		self.assertEqual(pag.title, "Meu título custom")

	def test_servico_titulo_manual_preservado(self):
		servico = create_test_servico()
		servico.title = "Meu título custom"
		servico.save(ignore_permissions=True)
		servico.reload()
		self.assertEqual(servico.title, "Meu título custom")

	def test_servico_titulo_composto(self):
		cliente = create_test_cliente()
		servico = create_test_servico(cliente=cliente.name, tipo="Consultoria")
		self.assertIn(cliente.nome, servico.title)
		self.assertIn("Consultoria", servico.title)
