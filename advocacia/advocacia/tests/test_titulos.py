"""Testes do padrão de títulos `{ID} — {descritor}`."""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import get_datetime, today

from advocacia.advocacia.titulos import TITLE_SEPARATOR, join_title_parts
from advocacia.advocacia.tests.test_setup import (
	create_test_acordo,
	create_test_hearing,
	create_test_client,
	create_test_legal_payment,
	create_test_registro_atos,
	create_test_legal_case,
	get_acordo_pagamentos,
)


def _titulo_composto(doc, descritor):
	return join_title_parts(doc.name, descritor)


class TestTitulosIdClient(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_registro_atos_titulo_distintivo_por_id(self):
		cliente = create_test_client()
		servico = create_test_legal_case(cliente=cliente.name)
		a1 = create_test_registro_atos(servico=servico.name)
		a2 = create_test_registro_atos(servico=servico.name)
		self.assertNotEqual(a1.title, a2.title)
		self.assertTrue(a1.title.startswith(a1.name))
		self.assertTrue(a2.title.startswith(a2.name))
		self.assertIn(cliente.client_name, a1.title)

	def test_registro_atos_after_insert_preenche_titulo(self):
		registro = create_test_registro_atos()
		self.assertTrue(registro.title)
		self.assertTrue(registro.title.startswith(registro.name))
		self.assertIn(TITLE_SEPARATOR, registro.title)

	def test_registro_atos_titulo_manual_preservado(self):
		registro = create_test_registro_atos()
		descritor = "Meu título custom"
		registro.title = descritor
		registro.save(ignore_permissions=True)
		registro.reload()
		self.assertEqual(registro.title, _titulo_composto(registro, descritor))

	def test_registro_atos_titulo_manual_no_insert(self):
		servico = create_test_legal_case()
		descritor = "Custom no insert"
		registro = frappe.get_doc(
			{
				"doctype": "Service Record",
				"legal_case": servico.name,
				"title": descritor,
				"acts": [{"act_date": today(), "type": "Inicial", "amount": 100}],
			}
		).insert(ignore_permissions=True)
		self.assertEqual(registro.title, _titulo_composto(registro, descritor))

	def test_hearing_titulo_distintivo_por_id(self):
		servico = create_test_legal_case()
		a1 = create_test_hearing(
			servico=servico.name,
			hearing_datetime=get_datetime("2026-03-15 10:00:00"),
		)
		a2 = create_test_hearing(
			servico=servico.name,
			hearing_datetime=get_datetime("2026-03-15 10:00:00"),
		)
		self.assertNotEqual(a1.title, a2.title)
		self.assertTrue(a1.title.startswith(a1.name))

	def test_hearing_titulo_manual_preservado(self):
		aud = create_test_hearing()
		descritor = "Meu título custom"
		aud.title = descritor
		aud.save(ignore_permissions=True)
		aud.reload()
		self.assertEqual(aud.title, _titulo_composto(aud, descritor))

	def test_legal_payment_titulo_distintivo_por_id(self):
		acordo = create_test_acordo(num_parcelas=2, total_amount=1000)
		pagamentos = get_acordo_pagamentos(acordo.name)
		self.assertGreaterEqual(len(pagamentos), 2)
		p1 = frappe.get_doc("Legal Payment", pagamentos[0].name)
		p2 = frappe.get_doc("Legal Payment", pagamentos[1].name)
		self.assertNotEqual(p1.title, p2.title)
		self.assertTrue(p1.title.startswith(p1.name))

	def test_legal_payment_titulo_manual_preservado(self):
		pag = create_test_legal_payment()
		descritor = "Meu título custom"
		pag.title = descritor
		pag.save(ignore_permissions=True)
		pag.reload()
		self.assertEqual(pag.title, _titulo_composto(pag, descritor))

	def test_legal_case_titulo_manual_preservado(self):
		servico = create_test_legal_case()
		descritor = "Meu título custom"
		servico.title = descritor
		servico.save(ignore_permissions=True)
		servico.reload()
		self.assertEqual(servico.title, _titulo_composto(servico, descritor))

	def test_legal_case_titulo_id_cliente(self):
		cliente = create_test_client()
		servico = create_test_legal_case(cliente=cliente.name, type="Consultoria")
		self.assertIn(servico.name, servico.title)
		self.assertIn(cliente.client_name, servico.title)
