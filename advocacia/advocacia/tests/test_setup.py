"""Helpers e fixtures reutilizáveis para testes do app advocacia."""

import random

import frappe
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
		"doctype": "Parcela de Honorarios",
		"vencimento": vencimento,
		"valor_total": flt(valor_total),
		"valor_advogada": 0,
		"valor_cliente": 0,
		"valor_sucumbência": 0,
		"status": "Pendente",
		"descrição": f"Parcela {idx}",
	}


def create_test_cliente(tipo_pessoa="Pessoa Física", nome=None, cpf=None, cnpj=None, **kwargs):
	"""Cria Cliente de teste. Retorna doc inserido."""
	if not nome:
		nome = _uid("Cliente Teste")
	data = {
		"doctype": "Cliente",
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


def create_test_servico(cliente=None, tipo="Consultoria", numero_processo=None, **kwargs):
	"""Cria Servico de teste. Retorna doc inserido."""
	if not cliente:
		cliente = create_test_cliente().name
	data = {
		"doctype": "Servico",
		"cliente": cliente,
		"tipo": tipo,
		"status": "Em andamento",
	}
	if numero_processo is None and tipo == "Processo Judicial":
		data["numero_processo"] = _gerar_cnj_valido()
	elif numero_processo is not None:
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
	"""Cria Acordo com parcelas na child table table_ztjx."""
	if not servico:
		servico_doc = create_test_servico()
		servico = servico_doc.name
	cliente = frappe.db.get_value("Servico", servico, "cliente")

	if parcelas is None and num_parcelas:
		valor_parcela = flt(valor_total) / num_parcelas
		parcelas = [
			_parcela_row(add_months(today(), i), valor_parcela, i + 1)
			for i in range(num_parcelas)
		]

	doc = frappe.get_doc(
		{
			"doctype": "Acordo de Honorarios Processuais",
			"servico": servico,
			"cliente": cliente,
			"modo_honorarios": modo,
			"tipo_de_cobrança": tipo_cobranca,
			"valor_total_do_acordo": valor_total,
			"número_de_parcelas": num_parcelas,
			"data_primeira_parcela": today(),
			"table_ztjx": parcelas or [],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_pagamento(
	servico=None,
	cliente=None,
	valor=1000,
	data_vencimento=None,
	status="Pendente",
	acordo=None,
	tipo_origem="Honorários (Parcela)",
	**kwargs,
):
	"""Cria Pagamento de honorários vinculado a acordo (via sync se necessário)."""
	if acordo:
		servico = servico or frappe.db.get_value("Acordo de Honorarios Processuais", acordo, "servico")
		cliente = cliente or frappe.db.get_value("Acordo de Honorarios Processuais", acordo, "cliente")
	elif not servico:
		acordo_doc = create_test_acordo(num_parcelas=1, valor_total=valor)
		acordo = acordo_doc.name
		servico = acordo_doc.servico
		cliente = acordo_doc.cliente
		pagamentos = frappe.get_all("Pagamento", filters={"acordo": acordo}, pluck="name")
		if pagamentos:
			doc = frappe.get_doc("Pagamento", pagamentos[0])
			if status != "Pendente":
				doc.status = status
				doc.save(ignore_permissions=True)
			return doc
	else:
		cliente = cliente or frappe.db.get_value("Servico", servico, "cliente")

	data = {
		"doctype": "Pagamento",
		"servico": servico,
		"cliente": cliente,
		"valor": valor,
		"data_vencimento": data_vencimento or today(),
		"status": status,
		"tipo_origem": tipo_origem,
		"acordo": acordo,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_audiencia(servico=None, data_hora=None, tipo="Conciliação", **kwargs):
	if not servico:
		servico = create_test_servico().name
	data = {
		"doctype": "Audiencia",
		"servico": servico,
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
		servico = create_test_servico().name
	data = {
		"doctype": "Controle de Prazos",
		"servico": servico,
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
		"doctype": "Despesa do Escritorio",
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
		servico = create_test_servico().name
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
			"doctype": "Registro de Atos",
			"servico": servico,
			"atos": atos,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


def create_test_tarefa(titulo=None, servico=None, **kwargs):
	data = {
		"doctype": "Tarefa",
		"titulo": titulo or _uid("Tarefa Teste"),
		"status": "Pendente",
		"servico": servico,
	}
	data.update(kwargs)
	doc = frappe.get_doc(data)
	doc.insert(ignore_permissions=True)
	return doc


def get_acordo_pagamentos(acordo_name):
	return frappe.get_all(
		"Pagamento",
		filters={"acordo": acordo_name, "tipo_origem": "Honorários (Parcela)"},
		fields=["name", "status", "parcela_origem_id", "valor"],
		order_by="creation asc",
	)
