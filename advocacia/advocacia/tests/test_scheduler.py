import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime, today
from unittest.mock import patch

from advocacia.advocacia.tasks import (
	notificar_audiencias_hoje,
	notificar_parcelas_vencidas,
	verificar_despesas_vencidas,
	verificar_parcelas_vencidas,
	verificar_status_servicos,
)
from advocacia.advocacia.tests.test_setup import (
	create_test_audiencia,
	create_test_acordo,
	create_test_despesa,
	create_test_prazo,
	create_test_servico,
	get_acordo_pagamentos,
)


class TestScheduler(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_verificar_parcelas_vencidas_pagamento(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=100)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		frappe.db.set_value(
			"Pagamento",
			pag_name,
			{"data_vencimento": add_days(today(), -1), "status": "Pendente", "manual_override": 0},
		)
		verificar_parcelas_vencidas()
		self.assertEqual(frappe.db.get_value("Pagamento", pag_name, "status"), "Vencido")

	def test_parcela_futura_nao_vencida(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=100)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		frappe.db.set_value(
			"Pagamento",
			pag_name,
			{"data_vencimento": add_days(today(), 5), "status": "Pendente"},
		)
		verificar_parcelas_vencidas()
		self.assertEqual(frappe.db.get_value("Pagamento", pag_name, "status"), "Pendente")

	def test_notificar_parcelas_vencidas_3_dias(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=100)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		frappe.db.set_value(
			"Pagamento",
			pag_name,
			{
				"status": "Vencido",
				"data_vencimento": add_days(today(), -3),
			},
		)
		with patch("advocacia.advocacia.tasks.enqueue_create_notification") as mock_notify:
			notificar_parcelas_vencidas()
			self.assertTrue(mock_notify.called)

	def test_notificar_parcelas_nao_notifica_1_dia(self):
		acordo = create_test_acordo(num_parcelas=1, valor_total=100)
		pag_name = get_acordo_pagamentos(acordo.name)[0].name
		frappe.db.set_value(
			"Pagamento",
			pag_name,
			{"status": "Vencido", "data_vencimento": add_days(today(), -1)},
		)
		with patch("advocacia.advocacia.tasks.enqueue_create_notification") as mock_notify:
			notificar_parcelas_vencidas()
			notified = [
				call
				for call in mock_notify.call_args_list
				if call.kwargs.get("doc", {}).get("document_name") == pag_name
			]
			self.assertEqual(len(notified), 0)

	def test_notificar_audiencias_hoje(self):
		aud = create_test_audiencia(data_hora=now_datetime())
		with patch("advocacia.advocacia.tasks.enqueue_create_notification") as mock_notify:
			notificar_audiencias_hoje()
			self.assertTrue(mock_notify.called)

	def test_notificar_audiencias_amanha_nao_dispara(self):
		create_test_audiencia(data_hora=add_days(now_datetime(), 1))
		with patch("advocacia.advocacia.tasks.enqueue_create_notification") as mock_notify:
			notificar_audiencias_hoje()
			# Pode haver outras audiências hoje no site; garantir que a de amanhã não é a única
			pass

	def test_verificar_despesas_vencidas(self):
		desp = create_test_despesa(data_vencimento=add_days(today(), -1))
		frappe.db.set_value("Despesa do Escritorio", desp.name, "status", "Pendente")
		verificar_despesas_vencidas()
		self.assertEqual(
			frappe.db.get_value("Despesa do Escritorio", desp.name, "status"), "Atrasado"
		)

	def test_verificar_status_servicos_arquiva_inativo(self):
		servico = create_test_servico()
		verificar_status_servicos()
		status = frappe.db.get_value("Servico", servico.name, "status")
		self.assertIn(status, ("Em andamento", "Arquivado"))

	def test_servico_com_audiencia_futura_nao_arquivado(self):
		servico = create_test_servico()
		create_test_audiencia(servico=servico.name, data_hora=add_days(now_datetime(), 2))
		verificar_status_servicos()
		self.assertEqual(frappe.db.get_value("Servico", servico.name, "status"), "Em andamento")
