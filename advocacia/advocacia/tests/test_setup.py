"""Helpers e fixtures reutilizáveis para testes do app advocacia."""

import random

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, flt, now_datetime, today

from advocacia.advocacia.validators import _calcular_dv_cnpj, _calcular_dv_cpf, _calcular_dv_cnj

# Documentos válidos fixos (usados em test_validators)
VALID_CPF = "529.982.247-25"
VALID_CPF_DIGITS = "52998224725"
VALID_CNPJ = "11.222.333/0001-81"
VALID_CNPJ_DIGITS = "11222333000181"
VALID_CNJ = "0000001-20.2024.8.26.0001"
VALID_CNJ_DIGITS = "00000012020248260001"
VALID_CELULAR = "11987654321"
VALID_FIXO = "1132345678"
VALID_EMAIL = "teste@example.com"


def _uid(prefix="Teste"):
	return f"{prefix} {frappe.generate_hash(length=8)}"


def ensure_test_document_category(category_name="Petição"):
	if not frappe.db.exists("Document Category", category_name):
		frappe.get_doc(
			{"doctype": "Document Category", "category_name": category_name}
		).insert(ignore_permissions=True)
	return category_name


def _gerar_cpf_valido():
	while True:
		base = "".join(str(random.randint(0, 9)) for _ in range(9))
		if len(set(base)) > 1:
			return base + _calcular_dv_cpf(base)


def _gerar_cnpj_valido():
	while True:
		base = "".join(str(random.randint(0, 9)) for _ in range(12))
		if len(set(base)) > 1:
			return base + _calcular_dv_cnpj(base)


def _gerar_cnj_valido():
	"""Gera CNJ válido único (ano 2024, tribunal 26)."""
	for _ in range(50):
		seq = f"{random.randint(1, 9999999):07d}"
		candidate = f"{seq}20248260001"
		dv = _calcular_dv_cnj(candidate)
		numero = f"{seq}{dv}20248260001"
		if len(numero) == 20:
			return numero
	return VALID_CNJ_DIGITS


def _parcela_row(vencimento, valor_total, idx=1):
	return {
		"doctype": "Fee Installment",
		"due_date": vencimento,
		"total_amount": flt(valor_total),
		"lawyer_amount": 0,
		"client_amount": 0,
		"contingency_amount": 0,
		"status": "Pendente",
		"description": f"Parcela {idx}",
	}


def create_test_client(person_type="Pessoa Física", client_name=None, cpf=None, cnpj=None, **kwargs):
	"""Cria Client de teste. Retorna doc inserido."""
	if not client_name:
		client_name = _uid("Client Teste")
	data = {
		"doctype": "Client",
		"person_type": person_type,
		"client_name": client_name,
	}
	if person_type == "Pessoa Física":
		data["cpf"] = cpf if cpf is not None else _gerar_cpf_valido()
	else:
		data["cnpj"] = cnpj if cnpj is not None else _gerar_cnpj_valido()
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_legal_case(cliente=None, type="Consultoria", case_number=None, **kwargs):
	"""Cria Legal Case de teste. Retorna doc inserido."""
	if not cliente:
		cliente = create_test_client().name
	data = {
		"doctype": "Legal Case",
		"client": cliente,
		"type": type,
		"status": "Em andamento",
	}
	if case_number is None and type == "Processo Judicial":
		data["case_number"] = _gerar_cnj_valido()
	elif case_number is not None:
		data["case_number"] = case_number
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_acordo(
	servico=None,
	modo="Honorários Diretos",
	tipo_cobranca="Valor fixo",
	total_amount=10000,
	num_parcelas=2,
	parcelas=None,
):
	"""Cria Acordo com parcelas na child table parcelas."""
	if not servico:
		servico_doc = create_test_legal_case()
		servico = servico_doc.name
	cliente = frappe.db.get_value("Legal Case", servico, "client")

	if parcelas is None and num_parcelas:
		valor_parcela = flt(total_amount) / num_parcelas
		parcelas = [
			_parcela_row(add_months(today(), i), valor_parcela, i + 1)
			for i in range(num_parcelas)
		]

	doc = frappe.get_doc(
		{
			"doctype": "Fee Agreement",
			"legal_case": servico,
			"client": cliente,
			"fee_mode": modo,
			"billing_type": tipo_cobranca,
			"total_agreement_value": total_amount,
			"installment_count": num_parcelas,
			"first_installment_date": today(),
			"fee_installments": parcelas or [],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_legal_payment(
	servico=None,
	cliente=None,
	amount=1000,
	due_date=None,
	status="Pendente",
	acordo=None,
	origin_type="Honorários (Parcela)",
	**kwargs,
):
	"""Cria Legal Payment de honorários vinculado a acordo (via sync se necessário)."""
	if acordo:
		servico = servico or frappe.db.get_value("Fee Agreement", acordo, "legal_case")
		cliente = cliente or frappe.db.get_value("Fee Agreement", acordo, "client")
	elif not servico:
		acordo_doc = create_test_acordo(num_parcelas=1, total_amount=amount)
		acordo = acordo_doc.name
		servico = acordo_doc.legal_case
		cliente = acordo_doc.client
		pagamentos = frappe.get_all("Legal Payment", filters={"fee_agreement": acordo}, pluck="name")
		if pagamentos:
			doc = frappe.get_doc("Legal Payment", pagamentos[0])
			if status != "Pendente":
				doc.status = status
				doc.save(ignore_permissions=True)
			return doc
	else:
		cliente = cliente or frappe.db.get_value("Legal Case", servico, "client")

	data = {
		"doctype": "Legal Payment",
		"legal_case": servico,
		"client": cliente,
		"amount": amount,
		"due_date": due_date or today(),
		"status": status,
		"origin_type": origin_type,
		"fee_agreement": acordo,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_hearing(servico=None, hearing_datetime=None, type="Conciliação", **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Hearing",
		"legal_case": servico,
		"hearing_datetime": hearing_datetime or now_datetime(),
		"type": type,
		"modality": "Presencial",
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_prazo(servico=None, due_date=None, description=None, **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Deadline",
		"legal_case": servico,
		"due_date": due_date or add_days(today(), 7),
		"description": description or _uid("Prazo Teste"),
		"priority": "Média",
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_despesa(description=None, category="Aluguel", amount=2500, due_date=None, is_recurring=0, **kwargs):
	data = {
		"doctype": "Office Expense",
		"description": description or _uid("Despesa Teste"),
		"category": category,
		"amount": amount,
		"due_date": due_date or today(),
		"is_recurring": is_recurring,
		"frequency": "Mensal" if is_recurring else None,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_registro_atos(servico=None, atos=None):
	if not servico:
		servico = create_test_legal_case().name
	if atos is None:
		atos = [
			{
				"act_date": today(),
				"type": "Inicial",
				"amount": 3000,
				"description": "Petição inicial teste",
			},
			{
				"act_date": today(),
				"type": "Audiência",
				"amount": 1500,
				"description": "Audiência teste",
			},
		]
	doc = frappe.get_doc(
		{
			"doctype": "Service Record",
			"legal_case": servico,
			"acts": atos,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_legal_task(subject=None, servico=None, **kwargs):
	data = {
		"doctype": "Legal Task",
		"subject": subject or _uid("Legal Task Teste"),
		"status": "Pendente",
		"legal_case": servico,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def get_acordo_pagamentos(acordo_name):
	return frappe.get_all(
		"Legal Payment",
		filters={"fee_agreement": acordo_name, "origin_type": "Honorários (Parcela)"},
		fields=["name", "status", "installment_origin_id", "amount"],
		order_by="creation asc",
	)


def create_test_court_cost(servico=None, description=None, type="Taxa Judicial", amount=500, **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Court Cost",
		"legal_case": servico,
		"description": description or _uid("Custa Teste"),
		"type": type,
		"amount": amount,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_case_communication(cliente=None, subject=None, type="Telefone", **kwargs):
	if not cliente:
		cliente = create_test_client().name
	data = {
		"doctype": "Case Communication",
		"client": cliente,
		"subject": subject or _uid("Comunicação Teste"),
		"type": type,
		"communication_date": now_datetime(),
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


class TestSetupInfrastructure(FrappeTestCase):
	def test_advocacia_roles_exist(self):
		for role in ("Advocacia User", "Advocacia Manager"):
			self.assertTrue(frappe.db.exists("Role", role), msg=f"Role {role} ausente")

	def test_kanban_board_exists(self):
		self.assertTrue(frappe.db.exists("Kanban Board", "Advocacia Tarefas"))
		board = frappe.get_doc("Kanban Board", "Advocacia Tarefas")
		self.assertEqual(board.reference_doctype, "Legal Task")
		self.assertEqual(board.field_name, "status")


def create_test_registro_horas(servico=None, activity=None, duration_minutes=60, **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Time Entry",
		"legal_case": servico,
		"entry_date": today(),
		"activity": activity or _uid("Atividade Teste"),
		"duration_minutes": duration_minutes,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc
