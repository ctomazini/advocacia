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
		"vencimento": vencimento,
		"valor_total": flt(valor_total),
		"valor_advogada": 0,
		"valor_cliente": 0,
		"contingency_amount": 0,
		"status": "Pendente",
		"description": f"Parcela {idx}",
	}


def create_test_client(tipo_pessoa="Pessoa Física", nome=None, cpf=None, cnpj=None, **kwargs):
	"""Cria Client de teste. Retorna doc inserido."""
	if not nome:
		nome = _uid("Client Teste")
	data = {
		"doctype": "Client",
		"tipo_pessoa": tipo_pessoa,
		"nome": nome,
	}
	if tipo_pessoa == "Pessoa Física":
		data["cpf"] = cpf if cpf is not None else _gerar_cpf_valido()
	else:
		data["cnpj"] = cnpj if cnpj is not None else _gerar_cnpj_valido()
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_legal_case(cliente=None, tipo="Consultoria", numero_processo=None, **kwargs):
	"""Cria Legal Case de teste. Retorna doc inserido."""
	if not cliente:
		cliente = create_test_client().name
	data = {
		"doctype": "Legal Case",
		"client": cliente,
		"tipo": tipo,
		"status": "Em andamento",
	}
	if numero_processo is None and tipo == "Processo Judicial":
		data["numero_processo"] = _gerar_cnj_valido()
	elif numero_processo is not None:
		if numero_processo == "":
			data["numero_processo"] = ""
		else:
			data["numero_processo"] = numero_processo
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_acordo(
	servico=None,
	modo="Honorários Diretos",
	tipo_cobranca="Valor fixo",
	valor_total=10000,
	num_parcelas=2,
	parcelas=None,
):
	"""Cria Acordo com parcelas na child table parcelas."""
	if not servico:
		servico_doc = create_test_legal_case()
		servico = servico_doc.name
	cliente = frappe.db.get_value("Legal Case", servico, "client")

	if parcelas is None and num_parcelas:
		valor_parcela = flt(valor_total) / num_parcelas
		parcelas = [
			_parcela_row(add_months(today(), i), valor_parcela, i + 1)
			for i in range(num_parcelas)
		]

	doc = frappe.get_doc(
		{
			"doctype": "Fee Agreement",
			"legal_case": servico,
			"client": cliente,
			"modo_honorarios": modo,
			"billing_type": tipo_cobranca,
			"valor_total_do_acordo": valor_total,
			"installment_count": num_parcelas,
			"data_primeira_parcela": today(),
			"fee_installments": parcelas or [],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_legal_payment(
	servico=None,
	cliente=None,
	valor=1000,
	data_vencimento=None,
	status="Pendente",
	acordo=None,
	tipo_origem="Honorários (Parcela)",
	**kwargs,
):
	"""Cria Legal Payment de honorários vinculado a acordo (via sync se necessário)."""
	if acordo:
		servico = servico or frappe.db.get_value("Fee Agreement", acordo, "legal_case")
		cliente = cliente or frappe.db.get_value("Fee Agreement", acordo, "client")
	elif not servico:
		acordo_doc = create_test_acordo(num_parcelas=1, valor_total=valor)
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
		"valor": valor,
		"data_vencimento": data_vencimento or today(),
		"status": status,
		"tipo_origem": tipo_origem,
		"fee_agreement": acordo,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_hearing(servico=None, data_hora=None, tipo="Conciliação", **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Hearing",
		"legal_case": servico,
		"data_hora": data_hora or now_datetime(),
		"tipo": tipo,
		"modalidade": "Presencial",
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_prazo(servico=None, data_prazo=None, descricao=None, **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Deadline",
		"legal_case": servico,
		"data_prazo": data_prazo or add_days(today(), 7),
		"descricao": descricao or _uid("Prazo Teste"),
		"prioridade": "Média",
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_despesa(descricao=None, categoria="Aluguel", valor=2500, data_vencimento=None, recorrente=0, **kwargs):
	data = {
		"doctype": "Office Expense",
		"descricao": descricao or _uid("Despesa Teste"),
		"categoria": categoria,
		"valor": valor,
		"data_vencimento": data_vencimento or today(),
		"recorrente": recorrente,
		"frequencia": "Mensal" if recorrente else None,
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
				"data": today(),
				"tipo": "Inicial",
				"valor": 3000,
				"descricao": "Petição inicial teste",
			},
			{
				"data": today(),
				"tipo": "Audiência",
				"valor": 1500,
				"descricao": "Audiência teste",
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


def create_test_legal_task(titulo=None, servico=None, **kwargs):
	data = {
		"doctype": "Legal Task",
		"titulo": titulo or _uid("Legal Task Teste"),
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
		filters={"fee_agreement": acordo_name, "tipo_origem": "Honorários (Parcela)"},
		fields=["name", "status", "parcela_origem_id", "valor"],
		order_by="creation asc",
	)


def create_test_court_cost(servico=None, descricao=None, tipo="Taxa Judicial", valor=500, **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Court Cost",
		"legal_case": servico,
		"descricao": descricao or _uid("Custa Teste"),
		"tipo": tipo,
		"valor": valor,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_case_communication(cliente=None, assunto=None, tipo="Telefone", **kwargs):
	if not cliente:
		cliente = create_test_client().name
	data = {
		"doctype": "Case Communication",
		"client": cliente,
		"assunto": assunto or _uid("Comunicação Teste"),
		"tipo": tipo,
		"data": now_datetime(),
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


def create_test_registro_horas(servico=None, atividade=None, duracao_minutos=60, **kwargs):
	if not servico:
		servico = create_test_legal_case().name
	data = {
		"doctype": "Time Entry",
		"legal_case": servico,
		"data": today(),
		"atividade": atividade or _uid("Atividade Teste"),
		"duracao_minutos": duracao_minutos,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc
