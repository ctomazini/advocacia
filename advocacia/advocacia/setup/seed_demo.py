"""Utilitário de seed para ambiente de desenvolvimento (NÃO usar em produção)."""

import frappe
from frappe.utils import add_days, add_months, flt, get_datetime, now_datetime, today

from advocacia.advocacia.financeiro import gerar_pagamento_atos, sincronizar_pagamentos_do_acordo
from advocacia.advocacia.tests.test_setup import VALID_CNJ, create_test_servico
from advocacia.advocacia.validators import _calcular_dv_cnj

# CPF/CNPJ canônicos válidos (passam validação Receita/CNJ do app)
CPF_ANA = "52998224725"
CPF_BRUNO = "11144477735"
CPF_CARLA = "39053344705"
CNPJ_ALFA = "11222333000181"
CNPJ_BETA = "45448325000170"  # base 45.448.325/0001 + DV válido (92 do prompt falha validação)

DOCTYPES_TRANSACIONAIS = [
	"Pagamento",
	"Registro de Atos",
	"Acordo de Honorarios Processuais",
	"Audiencia",
	"Controle de Prazos",
	"Tarefa",
	"Comunicacao",
	"Registro de Horas",
	"Custa Processual",
	"Despesa do Escritorio",
	"Servico",
	"Cliente",
]

DOCTYPES_CONTAGEM = DOCTYPES_TRANSACIONAIS + [
	"Comarca",
	"Vara",
	"Tribunal",
	"Fase Processual",
	"Template Documento",
	"Kit de Documentos",
]

ORDEM_DELETE = list(DOCTYPES_TRANSACIONAIS)


def reportar_contagens_demo():
	"""Fase 1: reporta quantidade de registros por DocType alvo."""
	for dt in DOCTYPES_CONTAGEM:
		try:
			print(f"{dt}: {frappe.db.count(dt)}")
		except Exception as exc:
			print(f"{dt}: ERRO {exc}")


def limpar_dados_demo():
	"""Apaga dados transacionais/cadastrais de demo (ordem respeita dependências)."""
	frappe.flags.in_test = True
	for dt in ORDEM_DELETE:
		try:
			frappe.db.delete(dt)
			print(f"limpo: {dt}")
		except Exception as exc:
			print(f"ERRO {dt}: {exc}")
			raise
	frappe.db.commit()
	for dt in ORDEM_DELETE:
		print(f"{dt}: {frappe.db.count(dt)}")



def _cnj_valido(seq):
	"""Gera CNJ válido (módulo 97) com sequência fixa para seed reprodutível."""
	seq_str = f"{int(seq):07d}"
	temp = f"{seq_str}0020248260001"
	dv = _calcular_dv_cnj(temp)
	return f"{seq_str}{dv}20248260001"


def _insert(doc_dict):
	"""Insert de seed em dev — ignore_permissions evita bloqueio por role no console."""
	doc = frappe.get_doc(doc_dict)
	doc.insert(ignore_permissions=True)
	return doc


def _get_or_create_catalog(doctype, name_field, name_value, doc_dict):
	existing = frappe.db.get_value(doctype, {name_field: name_value}, "name")
	if existing:
		return frappe.get_doc(doctype, existing)
	return _insert(doc_dict)


def _seed_catalogo():
	"""Catálogo auxiliar — cria entradas demo se ainda não existirem."""
	comarca_central = _get_or_create_catalog(
		"Comarca",
		"comarca_name",
		"Comarca Central",
		{
			"doctype": "Comarca",
			"comarca_name": "Comarca Central",
			"uf": "SP",
			"city": "Cidade Exemplo",
		},
	)
	comarca_norte = _get_or_create_catalog(
		"Comarca",
		"comarca_name",
		"Comarca Norte",
		{
			"doctype": "Comarca",
			"comarca_name": "Comarca Norte",
			"uf": "RS",
			"city": "Cidade Norte",
		},
	)

	tribunal = _get_or_create_catalog(
		"Tribunal",
		"tribunal_name",
		"Tribunal de Justiça Exemplo",
		{
			"doctype": "Tribunal",
			"tribunal_name": "Tribunal de Justiça Exemplo",
			"abbreviation": "TJE",
			"jurisdiction": "Estadual",
		},
	)

	varas = [
		_get_or_create_catalog(
			"Vara",
			"vara_name",
			"1ª Vara Cível Central",
			{
				"doctype": "Vara",
				"vara_name": "1ª Vara Cível Central",
				"comarca": comarca_central.name,
				"court_type": "Cível",
			},
		),
		_get_or_create_catalog(
			"Vara",
			"vara_name",
			"2ª Vara Cível Central",
			{
				"doctype": "Vara",
				"vara_name": "2ª Vara Cível Central",
				"comarca": comarca_central.name,
				"court_type": "Cível",
			},
		),
		_get_or_create_catalog(
			"Vara",
			"vara_name",
			"Vara Criminal Norte",
			{
				"doctype": "Vara",
				"vara_name": "Vara Criminal Norte",
				"comarca": comarca_norte.name,
				"court_type": "Criminal",
			},
		),
	]

	fases = []
	for idx, nome in enumerate(["Inicial", "Instrução", "Recursal"], start=1):
		fases.append(
			_get_or_create_catalog(
				"Fase Processual",
				"phase_name",
				nome,
				{
					"doctype": "Fase Processual",
					"phase_name": nome,
					"sort_order": idx,
				},
			)
		)

	# Template Documento exige Attach .docx — omitido no seed.
	return {
		"comarcas": [comarca_central, comarca_norte],
		"tribunal": tribunal,
		"varas": varas,
		"fases": fases,
	}


def _endereco_demo(tipo="Residencial", cidade="Cidade Exemplo", estado="SP"):
	return {
		"doctype": "Endereco Cliente",
		"tipo": tipo,
		"cep": "01001000",
		"logradouro": "Rua das Flores",
		"numero": "100",
		"bairro": "Centro",
		"cidade": cidade,
		"estado": estado,
		"principal": 1,
	}


def _contato_demo(nome, email):
	return {
		"doctype": "Contato Cliente",
		"nome": nome,
		"tipo": "Principal",
		"celular": "11987654321",
		"email": email,
	}


def _seed_clientes():
	clientes = []

	if not frappe.db.exists("Cliente", {"cpf": CPF_ANA}):
		clientes.append(
			_insert(
				{
					"doctype": "Cliente",
					"tipo_pessoa": "Pessoa Física",
					"nome": "Ana Souza",
					"cpf": CPF_ANA,
					"enderecos": [_endereco_demo()],
					"contatos": [_contato_demo("Ana Souza", "ana.souza@exemplo.com")],
				}
			)
		)

	if not frappe.db.exists("Cliente", {"cpf": CPF_BRUNO}):
		clientes.append(
			_insert(
				{
					"doctype": "Cliente",
					"tipo_pessoa": "Pessoa Física",
					"nome": "Bruno Lima",
					"cpf": CPF_BRUNO,
					"enderecos": [_endereco_demo(cidade="Porto Alegre", estado="RS")],
					"contatos": [_contato_demo("Bruno Lima", "bruno.lima@exemplo.com")],
				}
			)
		)

	if not frappe.db.exists("Cliente", {"cpf": CPF_CARLA}):
		clientes.append(
			_insert(
				{
					"doctype": "Cliente",
					"tipo_pessoa": "Pessoa Física",
					"nome": "Carla Mendes",
					"cpf": CPF_CARLA,
					"enderecos": [_endereco_demo(cidade="Curitiba", estado="PR")],
					"contatos": [_contato_demo("Carla Mendes", "carla.mendes@exemplo.com")],
				}
			)
		)

	if not frappe.db.exists("Cliente", {"cnpj": CNPJ_ALFA}):
		clientes.append(
			_insert(
				{
					"doctype": "Cliente",
					"tipo_pessoa": "Pessoa Jurídica",
					"nome": "Empresa Alfa Ltda",
					"nome_fantasia": "Alfa Serviços",
					"cnpj": CNPJ_ALFA,
					"representante": "Daniel Representante",
					"cpf_representante": CPF_ANA,
					"enderecos": [_endereco_demo(tipo="Comercial")],
					"contatos": [_contato_demo("Daniel Representante", "contato@alfa.exemplo.com")],
				}
			)
		)

	if not frappe.db.exists("Cliente", {"cnpj": CNPJ_BETA}):
		clientes.append(
			_insert(
				{
					"doctype": "Cliente",
					"tipo_pessoa": "Pessoa Jurídica",
					"nome": "Comércio Beta S.A.",
					"nome_fantasia": "Beta Comércio",
					"cnpj": CNPJ_BETA,
					"representante": "Elena Representante",
					"cpf_representante": CPF_BRUNO,
					"enderecos": [_endereco_demo(tipo="Comercial", cidade="Florianópolis", estado="SC")],
					"contatos": [_contato_demo("Elena Representante", "contato@beta.exemplo.com")],
				}
			)
		)

	if not clientes:
		clientes = [
			frappe.get_doc("Cliente", n)
			for n in frappe.get_all("Cliente", pluck="name", order_by="creation asc", limit=5)
		]
	return clientes


def _seed_servicos(clientes, catalogo):
	comarca = catalogo["comarcas"][0]
	tribunal = catalogo["tribunal"]
	vara = catalogo["varas"][0]
	fase = catalogo["fases"][0]
	specs = [
		(clientes[0], "Consultoria", {}),
		(clientes[0], "Processo Judicial", {"numero_processo": VALID_CNJ, "comarca": comarca.name, "vara": vara.name, "tribunal": tribunal.name, "fase_processual": fase.name}),
		(clientes[1], "Contrato", {}),
		(clientes[1], "Processo Judicial", {"numero_processo": _cnj_valido(2), "comarca": catalogo["comarcas"][1].name, "vara": catalogo["varas"][2].name, "tribunal": tribunal.name}),
		(clientes[2], "Administrativo", {}),
		(clientes[3], "Consultoria", {}),
		(clientes[3], "Processo Judicial", {"numero_processo": _cnj_valido(3), "comarca": comarca.name, "vara": catalogo["varas"][1].name, "tribunal": tribunal.name}),
		(clientes[4], "Diligência", {}),
	]

	servicos = []
	for cliente, tipo, extra in specs:
		servicos.append(
			create_test_servico(cliente=cliente.name, tipo=tipo, **extra)
		)
	return servicos


def _ato_row(data, tipo, valor, descricao):
	return {"data": data, "tipo": tipo, "valor": valor, "descricao": descricao}


def _seed_transacionais(servicos, clientes):
	# Registro de Atos — 3 do mesmo cliente (Ana) para validar títulos distintos por ID
	servico_ana = servicos[0]
	registros_atos = []
	for idx in range(3):
		registros_atos.append(
			_insert(
				{
					"doctype": "Registro de Atos",
					"servico": servico_ana.name,
					"data_abertura": add_days(today(), -10 + idx),
					"atos": [
						_ato_row(today(), "Inicial", 1000 + idx * 500, f"Petição demo {idx + 1}"),
						_ato_row(today(), "Defesa", 2500, f"Defesa demo {idx + 1}"),
					],
				}
			)
		)

	# Acordos + sync pagamentos
	acordos = []
	for servico, valor, parcelas in [
		(servicos[0], 10000, 3),
		(servicos[3], 6000, 2),
		(servicos[1], 2500, 1),
	]:
		valor_parcela = flt(valor) / parcelas
		acordo = _insert(
			{
				"doctype": "Acordo de Honorarios Processuais",
				"servico": servico.name,
				"modo_honorarios": "Honorários Diretos",
				"tipo_de_cobrança": "Valor fixo",
				"valor_total_do_acordo": valor,
				"número_de_parcelas": parcelas,
				"data_primeira_parcela": today(),
				"parcelas": [
					{
						"doctype": "Parcela de Honorarios",
						"vencimento": add_months(today(), i),
						"valor_total": valor_parcela,
						"valor_advogada": 0,
						"valor_cliente": 0,
						"valor_sucumbência": 0,
						"status": "Pendente",
						"descrição": f"Parcela {i + 1}",
					}
					for i in range(parcelas)
				],
			}
		)
		sincronizar_pagamentos_do_acordo(acordo)
		acordos.append(acordo)

	# Pagamento de atos a partir do primeiro registro
	gerar_pagamento_atos(registros_atos[0].name, data_vencimento=add_days(today(), 15))

	# Variar status de alguns pagamentos de honorários
	pagamentos = frappe.get_all(
		"Pagamento",
		filters={"tipo_origem": "Honorários (Parcela)"},
		fields=["name"],
		order_by="creation asc",
		limit=5,
	)
	if pagamentos:
		p1 = frappe.get_doc("Pagamento", pagamentos[0].name)
		p1.status = "Recebido"
		p1.data_recebimento = today()
		p1.valor_recebido = p1.valor
		p1.save(ignore_permissions=True)
	if len(pagamentos) > 1:
		frappe.db.set_value(
			"Pagamento",
			pagamentos[1].name,
			{"data_vencimento": add_days(today(), -7), "status": "Vencido"},
			update_modified=True,
		)

	# Audiências
	for servico, offset, modalidade, status_aud, tipo in [
		(servicos[0], -5, "Presencial", "Realizada", "Conciliação"),
		(servicos[1], 3, "Virtual", "Agendada", "Instrução"),
		(servicos[2], 10, "Híbrida", "Agendada", "Julgamento"),
		(servicos[4], -2, "Presencial", "Cancelada", "Conciliação"),
	]:
		_insert(
			{
				"doctype": "Audiencia",
				"servico": servico.name,
				"data_hora": get_datetime(add_days(today(), offset)),
				"tipo": tipo,
				"modalidade": modalidade,
				"status_aud": status_aud,
			}
		)

	# Prazos
	for servico, offset, prioridade, status, descricao in [
		(servicos[0], 2, "Alta", "Pendente", "Contestação prazo demo"),
		(servicos[1], 7, "Alta", "Pendente", "Recurso prazo demo"),
		(servicos[2], -1, "Média", "Vencido", "Manifestação vencida"),
		(servicos[3], 14, "Baixa", "Concluído", "Prazo concluído demo"),
	]:
		_insert(
			{
				"doctype": "Controle de Prazos",
				"servico": servico.name,
				"data_prazo": add_days(today(), offset),
				"descricao": descricao,
				"prioridade": prioridade,
				"status": status,
			}
		)

	# Tarefas
	for servico, titulo, status, prioridade in [
		(servicos[0], "Revisar petição inicial", "Em Andamento", "Alta"),
		(servicos[1], "Preparar parecer consultivo", "Pendente", "Normal"),
		(servicos[2], "Organizar documentos administrativos", "Pendente", "Normal"),
		(servicos[4], "Follow-up diligência externa", "Concluída", "Urgente"),
	]:
		_insert(
			{
				"doctype": "Tarefa",
				"servico": servico.name,
				"titulo": titulo,
				"status": status,
				"prioridade": prioridade,
				"data_limite": add_days(today(), 5),
			}
		)

	# Comunicações
	for cliente, servico, assunto, tipo in [
		(clientes[0], servicos[0], "Retorno sobre audiência", "Telefone"),
		(clientes[1], servicos[2], "Envio de documentos", "Email"),
		(clientes[3], servicos[5], "Reunião de alinhamento", "Reunião Virtual"),
	]:
		_insert(
			{
				"doctype": "Comunicacao",
				"cliente": cliente.name,
				"servico": servico.name,
				"assunto": assunto,
				"tipo": tipo,
				"data": now_datetime(),
				"resumo": "Registro fictício para demonstração do app.",
			}
		)

	# Registros de horas
	for servico, atividade, minutos in [
		(servicos[0], "Reunião com cliente", 90),
		(servicos[1], "Elaboração de parecer", 120),
		(servicos[3], "Análise processual", 60),
		(servicos[4], "Diligência externa", 45),
	]:
		_insert(
			{
				"doctype": "Registro de Horas",
				"servico": servico.name,
				"data": add_days(today(), -3),
				"atividade": atividade,
				"duracao_minutos": minutos,
			}
		)

	# Custas
	for servico, tipo, valor, descricao in [
		(servicos[0], "Taxa Judicial", 500, "Taxa distribuição demo"),
		(servicos[1], "Certidão", 120, "Certidão cartorial demo"),
		(servicos[3], "Correios", 80, "Envio AR demo"),
	]:
		_insert(
			{
				"doctype": "Custa Processual",
				"servico": servico.name,
				"tipo": tipo,
				"descricao": descricao,
				"valor": valor,
			}
		)

	# Despesas do escritório (sem cliente)
	for descricao, categoria, valor, offset, recorrente in [
		("Aluguel sala comercial", "Aluguel", 3500, 5, 1),
		("Conta de energia", "Energia", 450, 10, 0),
		("Assinatura software jurídico", "Software/Assinatura", 199, 15, 1),
		("Material de escritório", "Material de Escritório", 280, -3, 0),
	]:
		_insert(
			{
				"doctype": "Despesa do Escritorio",
				"descricao": descricao,
				"categoria": categoria,
				"valor": valor,
				"data_vencimento": add_days(today(), offset),
				"recorrente": recorrente,
				"frequencia": "Mensal" if recorrente else None,
			}
		)

	return {"registros_atos": registros_atos, "acordos": acordos}


def popular_dados_demo(force=False):
	"""Popula o site com dataset genérico coerente para testes visuais."""
	if not force and frappe.db.count("Cliente") > 0:
		print(
			"Seed abortado: já existem clientes. "
			"Execute limpar_dados_demo() antes ou use force=True."
		)
		return {"skipped": True}

	catalogo = _seed_catalogo()
	clientes = _seed_clientes()
	servicos = _seed_servicos(clientes, catalogo)
	resultado = _seed_transacionais(servicos, clientes)

	frappe.db.commit()

	resumo = {
		"clientes": frappe.db.count("Cliente"),
		"servicos": frappe.db.count("Servico"),
		"registro_de_atos": frappe.db.count("Registro de Atos"),
		"pagamentos": frappe.db.count("Pagamento"),
		"audiencias": frappe.db.count("Audiencia"),
		"prazos": frappe.db.count("Controle de Prazos"),
		"tarefas": frappe.db.count("Tarefa"),
		"comunicacoes": frappe.db.count("Comunicacao"),
		"horas": frappe.db.count("Registro de Horas"),
		"custas": frappe.db.count("Custa Processual"),
		"despesas": frappe.db.count("Despesa do Escritorio"),
		"atos_mesmo_cliente": len(resultado["registros_atos"]),
	}
	print("Seed concluído:", resumo)
	return resumo


def validar_seed_demo():
	"""Validação pós-seed: contagens e amostra de títulos."""
	for dt in [
		"Cliente",
		"Servico",
		"Registro de Atos",
		"Pagamento",
		"Audiencia",
		"Controle de Prazos",
		"Tarefa",
		"Despesa do Escritorio",
	]:
		print(f"{dt}: {frappe.db.count(dt)}")

	print("--- títulos Registro de Atos ---")
	rows = frappe.get_all("Registro de Atos", fields=["name", "title", "cliente"], order_by="name asc")
	for row in rows:
		print(row)
		if row.title and not row.title.startswith(row.name):
			print(f"AVISO: título fora do padrão ID — cliente em {row.name}")

	titles = [r.title for r in rows if r.title]
	if len(titles) != len(set(titles)):
		print("AVISO: títulos duplicados em Registro de Atos")
	else:
		print("OK: títulos distintos em Registro de Atos")

	return rows
