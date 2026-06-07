from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from advocacia.advocacia.notificacoes import notificar_prazos_diario
from advocacia.advocacia.tests.test_setup import create_test_prazo


class TestNotificacoes(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_fixture_prazo_vencendo_existe(self):
		if not frappe.db.exists("Notification", "Advocacia - Prazo vencendo"):
			self.skipTest("Fixture Notification Advocacia - Prazo vencendo não instalada")
		doc = frappe.get_doc("Notification", "Advocacia - Prazo vencendo")
		self.assertTrue(doc.enabled)

	def test_fixture_audiencia_amanha_existe(self):
		if not frappe.db.exists("Notification", "Advocacia - Hearing amanha"):
			self.skipTest("Fixture Notification Advocacia - Hearing amanha não instalada")
		doc = frappe.get_doc("Notification", "Advocacia - Hearing amanha")
		self.assertTrue(doc.enabled)

	@patch("frappe.sendmail")
	def test_notificar_prazos_diario_envia_email(self, mock_sendmail):
		create_test_prazo(data_prazo=add_days(today(), 1), dias_notificacao=3)
		notificar_prazos_diario()
		if mock_sendmail.called:
			kwargs = mock_sendmail.call_args.kwargs
			self.assertIn("recipients", kwargs)
			self.assertTrue(kwargs["recipients"])

	@patch("frappe.sendmail")
	@patch("advocacia.advocacia.notificacoes.frappe.get_all")
	def test_sem_prazos_urgentes_nao_envia(self, mock_get_all, mock_sendmail):
		mock_get_all.return_value = [
			frappe._dict(
				name="PRAZO-TEST-LONGO",
				servico="SERV-TEST",
				cliente="CLI-TEST",
				data_prazo=add_days(today(), 30),
				descricao="Prazo fora da janela",
				prioridade="Normal",
				responsavel=None,
				dias_notificacao=3,
			)
		]
		notificar_prazos_diario()
		mock_sendmail.assert_not_called()

	@patch("frappe.sendmail")
	def test_subject_contem_advocacia(self, mock_sendmail):
		create_test_prazo(data_prazo=today(), dias_notificacao=5)
		notificar_prazos_diario()
		if mock_sendmail.called:
			subject = mock_sendmail.call_args.kwargs.get("subject", "")
			self.assertIn("Advocacia", subject)
