"""
Demo data seeder for Advocacia app.
Seeds realistic Brazilian legal data for testing. NOT for production.

Usage:
	bench --site advocacia.local seed-demo-advocacia
	bench --site advocacia.local clear-demo-advocacia
	bench --site advocacia.local execute advocacia.advocacia.setup.seed_demo.seed_demo_data
"""

from __future__ import annotations

import os
import tempfile
from typing import Any

import frappe
from frappe.utils import add_days, add_months, flt, get_datetime, now_datetime, today

from advocacia.advocacia.financeiro import gerar_pagamento_atos, sincronizar_pagamentos_do_acordo
from advocacia.advocacia.tests.test_setup import create_test_legal_case
from advocacia.advocacia.validators import _calcular_dv_cnj, _calcular_dv_cnpj, _calcular_dv_cpf

DEMO_MARKER = "_DEMO_"

CPF_ANA = "52998224725"	 # reservado — não usar no seed (colide com testes/fixtures)


def _demo_cpf(seed: int) -> str:
	digits = [((seed * 7 + i * 3) % 9) + 1 for i in range(9)]
	base = "".join(str(d) for d in digits)
	return base + _calcular_dv_cpf(base)


def _demo_cnpj(seed: int) -> str:
	digits = [((seed * 11 + i * 5) % 9) + 1 for i in range(12)]
	base = "".join(str(d) for d in digits)
	return base + _calcular_dv_cnpj(base)


CREATION_ORDER = [
	"Jurisdiction",
	"Court",
	"Court Branch",
	"Case Phase",
	"Client",
	"Legal Case",
	"Fee Agreement",
	"Service Record",
	"Legal Payment",
	"Hearing",
	"Deadline",
	"Legal Task",
	"Case Communication",
	"Time Entry",
	"Court Cost",
	"Office Expense",
	"Document Template",
	"Document Kit",
]

TEARDOWN_ORDER = [
	"Time Entry",
	"Case Communication",
	"Legal Task",
	"Court Cost",
	"Office Expense",
	"Legal Payment",
	"Hearing",
	"Deadline",
	"Service Record",
	"Fee Agreement",
	"Legal Case",
	"Client",
	"Document Template",
	"Document Kit",
	"Court Branch",
	"Jurisdiction",
	"Court",
	"Case Phase",
]

DEMO_MARKER_FIELDS: dict[str, str] = {
	"Client": "client_name",
	"Legal Case": "remarks",
	"Fee Agreement": "remarks",
	"Service Record": "remarks",
	"Legal Payment": "description",
	"Hearing": "remarks",
	"Deadline": "description",
	"Legal Task": "subject",
	"Case Communication": "subject",
	"Time Entry": "activity",
	"Court Cost": "description",
	"Office Expense": "description",
}

AUTONAME_FIELD_DOCTYPES: dict[str, str] = {
	"Jurisdiction": "jurisdiction_name",
	"Court Branch": "court_branch_name",
	"Court": "court_name",
	"Case Phase": "case_phase_name",
	"Document Template": "title",
	"Document Kit": "title",
}

SERVICO_LINKED_DOCTYPES = (
	"Legal Payment",
	"Hearing",
	"Deadline",
	"Legal Task",
	"Case Communication",
	"Time Entry",
	"Court Cost",
	"Fee Agreement",
	"Service Record",
)

_refs: dict[str, Any] = {}


def seed_demo_data() -> int:
	"""Populate site with demo data. Idempotent — clears existing demo first."""
	_guard_production()
	clear_demo_data()
	_refs.clear()
	frappe.flags.in_demo_seed = True
	try:
		_seed_cadastros()
		_seed_clientes()
		_seed_servicos()
		_seed_acordos()
		_seed_registro_atos()
		_seed_pagamentos()
		_seed_audiencias()
		_seed_prazos()
		_seed_tarefas()
		_seed_comunicacoes()
		_seed_registro_horas()
		_seed_custas()
		_seed_despesas()
		_seed_templates()
	finally:
		frappe.flags.in_demo_seed = False

	if not getattr(frappe.flags, "in_test", False):
		frappe.db.commit()
	count = _count_demo_docs()
	frappe.logger().info(f"seed-demo: {count} documentos criados")
	return count


def clear_demo_data() -> int:
	"""Remove all documents created by seed_demo_data."""
	_guard_production()
	frappe.flags.in_demo_teardown = True
	total = 0
	try:
		demo_servicos = _get_demo_servico_names()
		demo_clientes = _get_demo_cliente_names()

		for dt in TEARDOWN_ORDER:
			if frappe.get_meta(dt).istable:
				continue
			names = _get_demo_doc_names(dt, demo_servicos, demo_clientes)
			if not names:
				continue
			try:
				frappe.db.delete(dt, {"name": ["in", names]})
				total += len(names)
			except Exception:
				for name in names:
					try:
						frappe.db.delete(dt, {"name": name})
						total += 1
					except Exception:
						frappe.log_error(title=f"Demo teardown: {dt} {name}")
	finally:
		frappe.flags.in_demo_teardown = False

	if total and not getattr(frappe.flags, "in_test", False):
		frappe.db.commit()
	elif total:
		frappe.db.commit()
		frappe.logger().info(f"clear-demo: {total} documentos removidos")
	return total


def _guard_production() -> None:
	site = frappe.local.site
	if site and ("prod" in site or "erp." in site):
		frappe.throw(
			f"seed-demo bloqueado em site de produção: {site}",
			title="Ambiente de Produção",
		)


def _count_demo_docs() -> int:
	total = 0
	for dt in CREATION_ORDER:
		if frappe.get_meta(dt).istable:
			continue
		total += _count_demo(doctype=dt)
	return total


def _demo_label(label: str) -> str:
	if DEMO_MARKER in label:
		return label
	return f"{label}{DEMO_MARKER}"


def _demo_text(text: str) -> str:
	return f"{DEMO_MARKER} {text}"


def _demo_exists(doctype: str, filters: dict) -> bool:
	return bool(frappe.get_all(doctype, filters=filters, limit=1))


def _insert(doc_dict: dict) -> frappe.model.document.Document:
	doc = frappe.get_doc(doc_dict)
	doc.insert(ignore_permissions=True)	 # setup: seed de demonstração em dev
	return doc


def _get_or_create(doctype: str, name_field: str, name_value: str, doc_dict: dict):
	if frappe.db.exists(doctype, {name_field: name_value}):
		return frappe.get_doc(doctype, {name_field: name_value})
	return _insert(doc_dict)


def _get_demo_cliente_names() -> list[str]:
	return frappe.get_all(
		"Client",
		filters={"client_name": ["like", f"%{DEMO_MARKER}%"]},
		pluck="name",
	)


def _get_demo_servico_names() -> list[str]:
	return frappe.get_all(
		"Legal Case",
		filters={"remarks": ["like", f"%{DEMO_MARKER}%"]},
		pluck="name",
	)


def _get_demo_doc_names(
	doctype: str,
	demo_servicos: list[str] | None = None,
	demo_clientes: list[str] | None = None,
) -> list[str]:
	names: set[str] = set()
	field = AUTONAME_FIELD_DOCTYPES.get(doctype)
	if field:
		names.update(
			frappe.get_all(doctype, filters={field: ["like", f"%{DEMO_MARKER}%"]}, pluck="name")
		)

	marker_field = DEMO_MARKER_FIELDS.get(doctype)
	if marker_field:
		names.update(
			frappe.get_all(
				doctype,
				filters={marker_field: ["like", f"%{DEMO_MARKER}%"]},
				pluck="name",
			)
		)

	if doctype in SERVICO_LINKED_DOCTYPES and demo_servicos:
		names.update(
			frappe.get_all(doctype, filters={"legal_case": ["in", demo_servicos]}, pluck="name")
		)

	return list(names)


def _count_demo(doctype: str) -> int:
	field = AUTONAME_FIELD_DOCTYPES.get(doctype)
	if field:
		return frappe.db.count(doctype, {field: ["like", f"%{DEMO_MARKER}%"]})
	marker = DEMO_MARKER_FIELDS.get(doctype)
	if marker:
		return frappe.db.count(doctype, {marker: ["like", f"%{DEMO_MARKER}%"]})
	if doctype in SERVICO_LINKED_DOCTYPES:
		servicos = _get_demo_servico_names()
		if not servicos:
			return 0
		return frappe.db.count(doctype, {"legal_case": ["in", servicos]})
	return 0


def _cnj_valido(seq: int) -> str:
	seq_str = f"{int(seq):07d}"
	temp = f"{seq_str}0020248260001"
	dv = _calcular_dv_cnj(temp)
	return f"{seq_str}{dv}20248260001"


def _endereco_demo(cidade: str = "Novo Hamburgo", estado: str = "RS", tipo: str = "Residencial"):
	return {
		"doctype": "Client Address",
		"type": tipo,
		"cep": "93510000",
		"street": "Rua das Flores",
		"number": "100",
		"neighborhood": "Centro",
		"city": cidade,
		"state": estado,
		"is_primary": 1,
	}


def _contato_demo(nome: str, email: str):
	return {
		"doctype": "Client Contact",
		"contact_name": nome,
		"type": "Principal",
		"mobile": "51987654321",
		"email": email,
	}


def _create_docx_file(paragraph: str = "Template demo {{ cliente }}") -> str | None:
	try:
		from docx import Document as DocxDocument
	except ImportError:
		return None

	tmp_path = None
	try:
		with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
			tmp_path = tmp.name
			doc = DocxDocument()
			doc.add_paragraph(paragraph)
			doc.save(tmp_path)

		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"demo_template_{frappe.generate_hash(length=6)}.docx",
				"is_private": 1,
			}
		)
		with open(tmp_path, "rb") as handle:
			file_doc.content = handle.read()
		file_doc.save(ignore_permissions=True)
		return file_doc.file_url
	finally:
		if tmp_path and os.path.exists(tmp_path):
			os.unlink(tmp_path)


# ─── Seeders ─────────────────────────────────────────────────────────


def _seed_cadastros() -> None:
	comarcas_data = [
		{"jurisdiction_name": _demo_label("Novo Hamburgo"), "uf": "RS", "city": "Novo Hamburgo"},
		{"jurisdiction_name": _demo_label("São Leopoldo"), "uf": "RS", "city": "São Leopoldo"},
		{"jurisdiction_name": _demo_label("Porto Alegre"), "uf": "RS", "city": "Porto Alegre"},
		{"jurisdiction_name": _demo_label("Canoas"), "uf": "RS", "city": "Canoas"},
	]
	comarcas = []
	for data in comarcas_data:
		comarcas.append(
			_get_or_create("Jurisdiction", "jurisdiction_name", data["jurisdiction_name"], {"doctype": "Jurisdiction", **data})
		)
	_refs["comarcas"] = comarcas

	tribunais_data = [
		{"court_name": _demo_label("TJRS"), "abbreviation": "TJRS", "jurisdiction": "Estadual"},
		{"court_name": _demo_label("TRF4"), "abbreviation": "TRF4", "jurisdiction": "Federal"},
		{"court_name": _demo_label("TRT4"), "abbreviation": "TRT4", "jurisdiction": "Trabalho"},
	]
	tribunais = []
	for data in tribunais_data:
		tribunais.append(
			_get_or_create("Court", "court_name", data["court_name"], {"doctype": "Court", **data})
		)
	_refs["tribunais"] = tribunais

	varas_data = [
		{"court_branch_name": _demo_label("1ª Court Branch Cível"), "jurisdiction": comarcas[0].name, "court_type": "Cível"},
		{"court_branch_name": _demo_label("2ª Court Branch Cível"), "jurisdiction": comarcas[1].name, "court_type": "Cível"},
		{"court_branch_name": _demo_label("Court Branch do Trabalho"), "jurisdiction": comarcas[2].name, "court_type": "Trabalho"},
		{"court_branch_name": _demo_label("JEC"), "jurisdiction": comarcas[3].name, "court_type": "Juizado Especial"},
	]
	varas = []
	for data in varas_data:
		varas.append(_get_or_create("Court Branch", "court_branch_name", data["court_branch_name"], {"doctype": "Court Branch", **data}))
	_refs["varas"] = varas

	fases_data = [
		("Distribuído", 1),
		("Em andamento", 2),
		("Aguardando audiência", 3),
		("Sentenciado", 4),
		("Arquivado", 5),
	]
	fases = []
	for nome, ordem in fases_data:
		case_phase_name = _demo_label(nome)
		fases.append(
			_get_or_create(
				"Case Phase",
				"case_phase_name",
				case_phase_name,
				{"doctype": "Case Phase", "case_phase_name": case_phase_name, "sort_order": ordem},
			)
		)
	_refs["fases"] = fases


def _seed_clientes() -> None:
	specs = [
		("Pessoa Física", _demo_label("Ana Souza"), _demo_cpf(20), None, "ana.souza@exemplo.com", "Novo Hamburgo"),
		("Pessoa Física", _demo_label("Bruno Lima"), _demo_cpf(21), None, "bruno.lima@exemplo.com", "São Leopoldo"),
		("Pessoa Física", _demo_label("Carla Mendes"), _demo_cpf(22), None, "carla.mendes@exemplo.com", "Porto Alegre"),
		("Pessoa Física", _demo_label("Diego Martins"), _demo_cpf(23), None, "diego.martins@exemplo.com", "Canoas"),
		("Pessoa Física", _demo_label("Fernanda Rocha"), _demo_cpf(24), None, "fernanda.rocha@exemplo.com", "Novo Hamburgo"),
		("Pessoa Física", _demo_label("Gabriela Pires"), _demo_cpf(25), None, "gabriela.pires@exemplo.com", "São Leopoldo"),
		("Pessoa Física", _demo_label("Hugo Teixeira"), _demo_cpf(26), None, "hugo.teixeira@exemplo.com", "Porto Alegre"),
		("Pessoa Jurídica", _demo_label("Empresa Alfa Ltda"), None, _demo_cnpj(20), "contato@alfa.exemplo.com", "Novo Hamburgo"),
		("Pessoa Jurídica", _demo_label("Comércio Beta S.A."), None, _demo_cnpj(21), "contato@beta.exemplo.com", "Canoas"),
		("Pessoa Jurídica", _demo_label("Indústria Gamma Ltda"), None, _demo_cnpj(22), "contato@gamma.exemplo.com", "Porto Alegre"),
	]
	clientes = []
	for tipo, nome, cpf, cnpj, email, cidade in specs:
		filters = {"client_name": nome}
		if frappe.db.exists("Client", filters):
			clientes.append(frappe.get_doc("Client", filters))
			continue
		data: dict[str, Any] = {
			"doctype": "Client",
			"person_type": tipo,
			"client_name": nome,
			"addresses": [_endereco_demo(cidade=cidade)],
			"contacts": [_contato_demo(nome.replace(DEMO_MARKER, "").strip(), email)],
		}
		if cpf:
			data["cpf"] = cpf
		if cnpj:
			data["cnpj"] = cnpj
			data["representative"] = "Representante Legal Demo"
			data["representative_cpf"] = _demo_cpf(27)
		clientes.append(_insert(data))
	_refs["clientes"] = clientes


def _seed_servicos() -> None:
	clientes = _refs["clientes"]
	comarcas = _refs["comarcas"]
	varas = _refs["varas"]
	tribunal = _refs["tribunais"][0]
	fases = _refs["fases"]
	marker_obs = _demo_text("Serviço de demonstração")

	specs = [
		(clientes[0], "Consultoria", {}),
		(clientes[0], "Processo Judicial", {"case_number": _cnj_valido(101), "jurisdiction": comarcas[0].name, "court_branch_link": varas[0].name, "court": tribunal.name, "case_phase": fases[0].name}),
		(clientes[1], "Processo Judicial", {"case_number": _cnj_valido(2), "jurisdiction": comarcas[1].name, "court_branch_link": varas[1].name, "court": tribunal.name, "case_phase": fases[1].name}),
		(clientes[2], "Administrativo", {}),
		(clientes[3], "Consultoria", {}),
		(clientes[4], "Processo Judicial", {"case_number": _cnj_valido(3), "jurisdiction": comarcas[2].name, "court_branch_link": varas[2].name, "court": tribunal.name, "case_phase": fases[2].name}),
		(clientes[5], "Diligência", {}),
		(clientes[6], "Processo Judicial", {"case_number": _cnj_valido(4), "jurisdiction": comarcas[3].name, "court_branch_link": varas[3].name, "court": tribunal.name, "case_phase": fases[3].name}),
		(clientes[7], "Consultoria", {}),
		(clientes[8], "Processo Judicial", {"case_number": _cnj_valido(5), "jurisdiction": comarcas[0].name, "court_branch_link": varas[0].name, "court": _refs["tribunais"][1].name}),
		(clientes[9], "Processo Judicial", {"case_number": _cnj_valido(6), "jurisdiction": comarcas[1].name, "court_branch_link": varas[1].name, "court": _refs["tribunais"][2].name, "case_phase": fases[4].name}),
		(clientes[0], "Contrato", {}),
		(clientes[1], "Consultoria", {}),
		(clientes[2], "Processo Judicial", {"case_number": _cnj_valido(7), "jurisdiction": comarcas[2].name, "court_branch_link": varas[2].name, "court": tribunal.name}),
		(clientes[3], "Diligência", {}),
		(clientes[4], "Administrativo", {}),
		(clientes[5], "Processo Judicial", {"case_number": _cnj_valido(8), "jurisdiction": comarcas[3].name, "court_branch_link": varas[3].name, "court": tribunal.name, "case_phase": fases[1].name}),
	]

	servicos = []
	for cliente, tipo, extra in specs:
		if frappe.db.exists("Legal Case", {"client": cliente.name, "remarks": marker_obs, "type": tipo}):
			continue
		servicos.append(
			create_test_legal_case(
				cliente=cliente.name,
				type=tipo,
				remarks=marker_obs,
				**extra,
			)
		)
	if len(servicos) < len(specs):
		# Recarrega todos os serviços demo se parte já existia
		servicos = [
			frappe.get_doc("Legal Case", n)
			for n in frappe.get_all(
				"Legal Case",
				filters={"remarks": ["like", f"%{DEMO_MARKER}%"]},
				pluck="name",
				order_by="creation asc",
			)
		]
	_refs["servicos"] = servicos


def _seed_acordos() -> None:
	servicos = _refs["servicos"]
	specs = [
		(servicos[0], 12000, 4),
		(servicos[1], 8000, 3),
		(servicos[3], 6000, 2),
		(servicos[5], 15000, 5),
		(servicos[7], 4500, 2),
		(servicos[9], 9000, 3),
		(servicos[11], 3000, 1),
		(servicos[13], 7200, 3),
	]
	acordos = []
	for servico, valor, parcelas in specs:
		if frappe.get_all(
			"Fee Agreement",
			filters={"legal_case": servico.name, "remarks": ["like", f"%{DEMO_MARKER}%"]},
			limit=1,
		):
			continue
		valor_parcela = flt(valor) / parcelas
		acordo = _insert(
			{
				"doctype": "Fee Agreement",
				"legal_case": servico.name,
				"fee_mode": "Honorários Diretos",
				"billing_type": "Valor fixo",
				"total_agreement_value": valor,
				"installment_count": parcelas,
				"first_installment_date": today(),
				"remarks": _demo_text("Acordo de honorários demo"),
				"fee_installments": [
					{
						"doctype": "Fee Installment",
						"due_date": add_months(today(), i),
						"total_amount": valor_parcela,
						"lawyer_amount": valor_parcela,
						"client_amount": 0,
						"contingency_amount": 0,
						"status": "Pendente",
						"description": _demo_text(f"Parcela {i + 1}"),
					}
					for i in range(parcelas)
				],
			}
		)
		sincronizar_pagamentos_do_acordo(acordo)
		acordos.append(acordo)
	_refs["acordos"] = acordos or [
		frappe.get_doc("Fee Agreement", n)
		for n in frappe.get_all(
			"Fee Agreement",
			filters={"remarks": ["like", f"%{DEMO_MARKER}%"]},
			pluck="name",
		)
	]


def _ato_row(data, tipo, valor, descricao):
	return {"act_date": data, "type": tipo, "amount": valor, "description": _demo_text(descricao)}


def _seed_registro_atos() -> None:
	servicos = _refs["servicos"][:6]
	registros = []
	for idx, servico in enumerate(servicos):
		if _demo_exists(
			"Service Record",
			{"legal_case": servico.name, "remarks": ["like", f"%{DEMO_MARKER}%"]},
		):
			continue
		registros.append(
			_insert(
				{
					"doctype": "Service Record",
					"legal_case": servico.name,
					"opening_date": add_days(today(), -10 + idx),
					"remarks": _demo_text(f"Registro de atos demo {idx + 1}"),
					"acts": [
						_ato_row(today(), "Inicial", 1000 + idx * 200, f"Petição {idx + 1}"),
						_ato_row(today(), "Defesa", 1500, f"Defesa {idx + 1}"),
					],
				}
			)
		)
	_refs["registros_atos"] = registros or [
		frappe.get_doc("Service Record", n)
		for n in frappe.get_all(
			"Service Record",
			filters={"remarks": ["like", f"%{DEMO_MARKER}%"]},
			pluck="name",
		)
	]
	if _refs["registros_atos"]:
		gerar_pagamento_atos(_refs["registros_atos"][0].name, due_date=add_days(today(), 15))


def _seed_pagamentos() -> None:
	"""Marca pagamentos sincronizados e varia status para cenários do painel."""
	for pag in frappe.get_all(
		"Legal Payment",
		filters={"legal_case": ["in", [s.name for s in _refs["servicos"]]]},
		fields=["name", "description"],
	):
		if DEMO_MARKER not in (pag.description or ""):
			frappe.db.set_value(
				"Legal Payment",
				pag.name,
				"description",
				_demo_text(pag.description or "Legal Payment demo"),
				update_modified=False,
			)

	pagamentos = frappe.get_all(
		"Legal Payment",
		filters={"description": ["like", f"%{DEMO_MARKER}%"]},
		pluck="name",
		order_by="creation asc",
	)
	if pagamentos:
		p1 = frappe.get_doc("Legal Payment", pagamentos[0])
		p1.status = "Recebido"
		p1.received_date = today()
		p1.received_amount = p1.amount
		p1.save(ignore_permissions=True)
	if len(pagamentos) > 1:
		frappe.db.set_value(
			"Legal Payment",
			pagamentos[1],
			{"due_date": add_days(today(), -7), "status": "Vencido"},
			update_modified=True,
		)
	if len(pagamentos) > 2:
		frappe.db.set_value(
			"Legal Payment",
			pagamentos[2],
			{"due_date": add_days(today(), -30), "status": "Vencido"},
			update_modified=True,
		)


def _seed_audiencias() -> None:
	servicos = _refs["servicos"]
	specs = [
		(servicos[0], -5, "Presencial", "Realizada", "Conciliação"),
		(servicos[1], 0, "Virtual", "Agendada", "Instrução"),
		(servicos[2], 1, "Híbrida", "Agendada", "Conciliação"),
		(servicos[3], 3, "Presencial", "Agendada", "Instrução"),
		(servicos[4], 7, "Virtual", "Agendada", "Julgamento"),
		(servicos[5], -2, "Presencial", "Cancelada", "Conciliação"),
		(servicos[6], -10, "Presencial", "Realizada", "Instrução"),
		(servicos[7], 14, "Híbrida", "Agendada", "Conciliação"),
		(servicos[8], 0, "Virtual", "Agendada", "Instrução"),
		(servicos[9], 2, "Presencial", "Agendada", "Julgamento"),
		(servicos[10], -1, "Presencial", "Adiada", "Conciliação"),
		(servicos[11], 5, "Virtual", "Agendada", "Instrução"),
	]
	for servico, offset, modalidade, status_aud, tipo in specs:
		if _demo_exists(
			"Hearing",
			{"legal_case": servico.name, "type": tipo, "remarks": ["like", f"%{DEMO_MARKER}%"]},
		):
			continue
		_insert(
			{
				"doctype": "Hearing",
				"legal_case": servico.name,
				"hearing_datetime": get_datetime(add_days(today(), offset)),
				"type": tipo,
				"modality": modalidade,
				"status": status_aud,
				"remarks": _demo_text(f"Audiência {tipo} demo"),
			}
		)


def _seed_prazos() -> None:
	servicos = _refs["servicos"]
	specs = [
		(servicos[0], -5, "Alta", "Vencido", "Contestação vencida"),
		(servicos[1], 1, "Alta", "Pendente", "Recurso urgente"),
		(servicos[2], 2, "Alta", "Pendente", "Manifestação"),
		(servicos[3], 3, "Alta", "Pendente", "Embargos"),
		(servicos[4], 7, "Média", "Pendente", "Recurso ordinário"),
		(servicos[5], -1, "Média", "Vencido", "Manifestação vencida"),
		(servicos[6], 14, "Baixa", "Pendente", "Prazo futuro"),
		(servicos[7], 0, "Alta", "Pendente", "Prazo fatal hoje"),
		(servicos[8], 21, "Baixa", "Pendente", "Contrarrazões"),
		(servicos[9], -3, "Alta", "Vencido", "Agravo vencido"),
	]
	for servico, offset, prioridade, status, descricao in specs:
		if _demo_exists(
			"Deadline",
			{"legal_case": servico.name, "description": ["like", f"%{DEMO_MARKER}%"]},
		):
			continue
		_insert(
			{
				"doctype": "Deadline",
				"legal_case": servico.name,
				"due_date": add_days(today(), offset),
				"description": _demo_text(descricao),
				"priority": prioridade,
				"status": status,
			}
		)


def _seed_tarefas() -> None:
	servicos = _refs["servicos"]
	specs = [
		(servicos[0], "Revisar petição inicial", "Em Andamento", "Alta", 5),
		(servicos[1], "Preparar parecer consultivo", "Pendente", "Normal", 3),
		(servicos[2], "Organizar documentos", "Pendente", "Normal", 7),
		(servicos[3], "Follow-up cliente", "Concluída", "Urgente", -2),
		(servicos[4], "Elaborar recurso", "Em Andamento", "Alta", 2),
		(servicos[5], "Análise jurisprudencial", "Pendente", "Normal", 10),
		(servicos[6], "Protocolar petição", "Pendente", "Urgente", 1),
		(servicos[7], "Reunião de estratégia", "Concluída", "Normal", -5),
		(servicos[8], "Cobrar documentos", "Pendente", "Alta", -1),
		(servicos[9], "Atualizar andamento", "Em Andamento", "Normal", 4),
	]
	for servico, titulo, status, prioridade, offset in specs:
		if _demo_exists("Legal Task", {"legal_case": servico.name, "subject": ["like", f"%{DEMO_MARKER}%"]}):
			continue
		_insert(
			{
				"doctype": "Legal Task",
				"legal_case": servico.name,
				"subject": _demo_text(titulo),
				"status": status,
				"priority": prioridade,
				"due_date": add_days(today(), offset),
			}
		)


def _seed_comunicacoes() -> None:
	clientes = _refs["clientes"]
	servicos = _refs["servicos"]
	specs = [
		(clientes[0], servicos[0], "Retorno sobre audiência", "Telefone"),
		(clientes[1], servicos[2], "Envio de documentos", "Email"),
		(clientes[3], servicos[5], "Reunião de alinhamento", "Reunião Virtual"),
		(clientes[4], servicos[6], "WhatsApp — prazo fatal", "WhatsApp"),
		(clientes[5], servicos[7], "Contato sobre custas", "Telefone"),
		(clientes[6], servicos[8], "E-mail com proposta", "Email"),
		(clientes[7], servicos[9], "Ligação sobre honorários", "Telefone"),
		(clientes[8], servicos[min(10, len(servicos) - 1)], "Atualização processual", "Outro"),
	]
	for cliente, servico, assunto, tipo in specs:
		if _demo_exists("Case Communication", {"subject": ["like", f"%{DEMO_MARKER}%"], "legal_case": servico.name}):
			continue
		_insert(
			{
				"doctype": "Case Communication",
				"client": cliente.name,
				"legal_case": servico.name,
				"subject": _demo_text(assunto),
				"type": tipo,
				"communication_date": now_datetime(),
				"summary": _demo_text("Comunicação fictícia para demonstração."),
			}
		)


def _seed_registro_horas() -> None:
	servicos = _refs["servicos"][:5]
	specs = [
		(servicos[0], "Reunião com cliente", 90),
		(servicos[1], "Elaboração de parecer", 120),
		(servicos[2], "Análise processual", 60),
		(servicos[3], "Diligência externa", 45),
		(servicos[4], "Redação de petição", 150),
	]
	for servico, atividade, minutos in specs:
		if _demo_exists(
			"Time Entry",
			{"legal_case": servico.name, "activity": ["like", f"%{DEMO_MARKER}%"]},
		):
			continue
		_insert(
			{
				"doctype": "Time Entry",
				"legal_case": servico.name,
				"entry_date": add_days(today(), -3),
				"activity": _demo_text(atividade),
				"duration_minutes": minutos,
			}
		)


def _seed_custas() -> None:
	servicos = _refs["servicos"][:5]
	specs = [
		(servicos[0], "Taxa Judicial", 500, "Taxa distribuição"),
		(servicos[1], "Certidão", 120, "Certidão cartorial"),
		(servicos[2], "Correios", 80, "Envio AR"),
		(servicos[3], "Perícia", 2500, "Honorários periciais"),
		(servicos[4], "Taxa Judicial", 350, "Custas recursais"),
	]
	for servico, tipo, valor, descricao in specs:
		if _demo_exists(
			"Court Cost",
			{"legal_case": servico.name, "description": ["like", f"%{DEMO_MARKER}%"]},
		):
			continue
		_insert(
			{
				"doctype": "Court Cost",
				"legal_case": servico.name,
				"type": tipo,
				"description": _demo_text(descricao),
				"amount": valor,
			}
		)


def _seed_despesas() -> None:
	specs = [
		("Aluguel sala comercial", "Aluguel", 3500, 5, 1),
		("Conta de energia", "Energia", 450, 10, 0),
		("Assinatura software jurídico", "Software/Assinatura", 199, 15, 1),
	]
	for descricao, categoria, valor, offset, recorrente in specs:
		marked = _demo_text(descricao)
		if frappe.db.exists("Office Expense", {"description": marked}):
			continue
		_insert(
			{
				"doctype": "Office Expense",
				"description": marked,
				"category": categoria,
				"amount": valor,
				"due_date": add_days(today(), offset),
				"is_recurring": recorrente,
				"frequency": "Mensal" if recorrente else None,
			}
		)


def _seed_templates() -> None:
	file_url = _create_docx_file("Procuração demo {{ cliente }}")
	if not file_url:
		frappe.log_error("python-docx indisponível — templates demo omitidos")
		return

	templates = []
	for titulo, tipo in [
		(_demo_label("Procuração Ad Judicia"), "Contrato"),
		(_demo_label("Cobrança de Honorários"), "Contrato"),
	]:
		if frappe.db.exists("Document Template", titulo):
			templates.append(titulo)
			continue
		doc = _insert(
			{
				"doctype": "Document Template",
				"title": titulo,
				"document_type": tipo,
				"description": _demo_text(f"Modelo {tipo}"),
				"template_file": file_url,
				"enabled": 1,
			}
		)
		templates.append(doc.name)

	kit_titulo = _demo_label("Kit Inicial Processual")
	if not frappe.db.exists("Document Kit", kit_titulo):
		_insert(
			{
				"doctype": "Document Kit",
				"title": kit_titulo,
				"description": _demo_text("Kit de documentos para abertura de processo"),
				"enabled": 1,
				"templates": [{"template": t, "display_order": i + 1} for i, t in enumerate(templates)],
			}
		)


# ─── Aliases legados (console dev) ─────────────────────────────────────


def popular_dados_demo(force=False):
	"""Alias legado — use seed_demo_data()."""
	if not force and _count_demo_docs() > 0:
		print("Seed abortado: dados demo já existem. Use clear_demo_data() ou force=True.")
		return {"skipped": True}
	return {"count": seed_demo_data()}


def limpar_dados_demo():
	"""Alias legado — use clear_demo_data()."""
	return clear_demo_data()


def reportar_contagens_demo():
	for dt in CREATION_ORDER:
		if not frappe.get_meta(dt).istable:
			print(f"{dt}: {_count_demo(doctype=dt)} demo / {frappe.db.count(dt)} total")


def validar_seed_demo():
	reportar_contagens_demo()
	rows = frappe.get_all(
		"Service Record",
		filters={"remarks": ["like", f"%{DEMO_MARKER}%"]},
		fields=["name", "title", "client"],
		order_by="name asc",
	)
	for row in rows:
		print(row)
	return rows
