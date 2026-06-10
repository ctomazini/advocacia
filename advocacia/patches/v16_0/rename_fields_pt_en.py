"""Mapa canônico do rename de fieldnames PT→EN (jun/2026).

Fonte única usada pelos patches `rename_fields_*` (um por DocType) e pelo
script `scripts/rename_fieldnames_pt_en.py` que reescreveu JSONs e código.

Decisões de nomenclatura (aprovadas):
- data_hora → hearing_datetime (datetime colide com módulo Python / reserved SQL)
- advogada/cliente em valores → lawyer_* / client_*
- observacoes/observacao → remarks
- tipo → type; compostos: document_type, person_type, origin_type
- Legal Task.titulo → subject (colisão: Legal Task já possui `title` composto)
- Identificadores brasileiros mantidos: cpf, cnpj, cep, oab, rg, uf
"""

import frappe

# Campos Button/HTML não têm coluna no banco — o guard has_column os ignora.
RENAMES: dict[str, dict[str, str]] = {
	"Case Communication": {
		"data": "communication_date",
		"tipo": "type",
		"assunto": "subject",
		"resumo": "summary",
		"proximos_passos": "next_steps",
		"gerar_tarefa": "generate_task",
	},
	"Client": {
		"tipo_pessoa": "person_type",
		"nome": "client_name",
		"nome_fantasia": "trade_name",
		"nacionalidade": "nationality",
		"estado_civil": "marital_status",
		"profissao": "occupation",
		"representante": "representative",
		"cpf_representante": "representative_cpf",
		"cargo_representante": "representative_role",
		"nacionalidade_pj": "representative_nationality",
		"observacoes": "remarks",
	},
	"Client Address": {
		"tipo": "type",
		"logradouro": "street",
		"numero": "number",
		"complemento": "complement",
		"bairro": "neighborhood",
		"cidade": "city",
		"estado": "state",
		"principal": "is_primary",
	},
	"Client Contact": {
		"nome": "contact_name",
		"tipo": "type",
		"telefone": "phone",
		"celular": "mobile",
		"observacao": "remarks",
	},
	"Court Cost": {
		"tipo": "type",
		"descricao": "description",
		"valor": "amount",
		"data_pagamento": "payment_date",
		"repassar_cliente": "bill_to_client",
		"data_repasse": "transfer_date",
		"forma_pagamento": "payment_method",
		"comprovante": "receipt",
		"observacoes": "remarks",
	},
	"Deadline": {
		"data_prazo": "due_date",
		"descricao": "description",
		"prioridade": "priority",
		"responsavel": "responsible",
		"dias_notificacao": "notification_days",
		"observacoes": "remarks",
	},
	"Document Kit": {
		"titulo": "title",
		"descricao": "description",
		"habilitado": "enabled",
	},
	"Document Kit Item": {
		"ordem": "display_order",
	},
	"Document Template": {
		"titulo": "title",
		"tipo_documento": "document_type",
		"descricao": "description",
		"habilitado": "enabled",
		"arquivo": "template_file",
		"ver_placeholders": "show_placeholders",
	},
	"Fee Agreement": {
		"modo_honorarios": "fee_mode",
		"valor_total_do_acordo": "total_agreement_value",
		"percentual_advogada": "lawyer_percentage",
		"valor_fixo_de_honorarios": "fixed_fee_amount",
		"valor_advogada": "lawyer_amount",
		"percentual_cliente": "client_percentage",
		"valor_cliente": "client_amount",
		"data_primeira_parcela": "first_installment_date",
		"valor_da_parcela": "installment_amount",
		"gerar_parcelas": "generate_installments",
		"total_advogada": "lawyer_total",
		"total_cliente": "client_total",
	},
	"Fee Installment": {
		"vencimento": "due_date",
		"valor_total": "total_amount",
		"valor_advogada": "lawyer_amount",
		"valor_cliente": "client_amount",
		"parcela_origem_id": "installment_origin_id",
		"data_recebimento": "received_date",
		"data_repasse": "transfer_date",
		"forma_recebimento": "payment_method",
		"observacao": "remarks",
	},
	"Hearing": {
		"data_hora": "hearing_datetime",
		"status_aud": "status",
		"tipo": "type",
		"modalidade": "modality",
		"resultado": "outcome",
		"observacoes": "remarks",
	},
	"Legal Act Item": {
		"data": "act_date",
		"tipo": "type",
		"valor": "amount",
	},
	"Legal Case": {
		"tipo": "type",
		"data_abertura": "opening_date",
		"numero_processo": "case_number",
		"numeracao_legada": "legacy_numbering",
		"parte_contraria": "opposing_party",
		"valor_causa": "case_value",
		"observacoes": "remarks",
	},
	"Legal Payment": {
		"tipo_origem": "origin_type",
		"numero_parcela": "installment_number",
		"descricao": "description",
		"parcela_origem_id": "installment_origin_id",
		"sincronizado_em": "synced_at",
		"valor": "amount",
		"valor_recebido": "received_amount",
		"data_vencimento": "due_date",
		"data_recebimento": "received_date",
		"observacoes": "remarks",
		"comprovante": "receipt",
	},
	"Legal Task": {
		"titulo": "subject",
		"prioridade": "priority",
		"data_limite": "due_date",
		"descricao": "description",
		"responsavel": "responsible",
		"data_conclusao": "completion_date",
	},
	"Office Expense": {
		"descricao": "description",
		"categoria": "category",
		"valor": "amount",
		"data_vencimento": "due_date",
		"data_pagamento": "payment_date",
		"forma_pagamento": "payment_method",
		"recorrente": "is_recurring",
		"frequencia": "frequency",
		"proximo_vencimento": "next_due_date",
		"comprovante": "receipt",
		"observacoes": "remarks",
	},
	"Office Settings": {
		"razao_social": "company_name",
		"registro_sia": "sia_registration",
		"advogada": "lawyer_name",
		"endereco": "address",
	},
	"Service Record": {
		"data_abertura": "opening_date",
		"total_pendente": "pending_total",
		"total_cobrado": "billed_total",
		"total_geral": "grand_total",
		"data_vencimento_cobranca": "billing_due_date",
		"gerar_cobranca": "generate_billing",
		"observacoes": "remarks",
	},
	"Time Entry": {
		"data": "entry_date",
		"responsavel": "responsible",
		"hora_inicio": "start_time",
		"hora_fim": "end_time",
		"duracao_minutos": "duration_minutes",
		"duracao_horas": "duration_hours",
		"atividade": "activity",
		"categoria": "category",
		"descricao": "description",
		"cobravel": "billable",
		"timer_inicio": "timer_start",
		"timer_ativo": "timer_active",
	},
}

SINGLES = {"Office Settings"}


def rename_doctype_columns(doctype: str) -> None:
	"""Renomeia colunas PT→EN de um DocType de forma idempotente."""
	renames = RENAMES[doctype]
	if doctype in SINGLES:
		_rename_singles_rows(doctype, renames)
	else:
		if not frappe.db.table_exists(doctype):
			return
		for old, new in renames.items():
			if frappe.db.has_column(doctype, old) and not frappe.db.has_column(doctype, new):
				frappe.db.rename_column(doctype, old, new)
	# patch pre_model_sync: persistir rename antes do model sync (permitido em patches)
	frappe.db.commit()


def _rename_singles_rows(doctype: str, renames: dict[str, str]) -> None:
	"""Single DocType: dados vivem em tabSingles — renomeia a chave `field`."""
	for old, new in renames.items():
		has_old = frappe.db.sql(
			"select 1 from `tabSingles` where doctype=%s and field=%s", (doctype, old)
		)
		if not has_old:
			continue
		has_new = frappe.db.sql(
			"select 1 from `tabSingles` where doctype=%s and field=%s", (doctype, new)
		)
		if has_new:
			frappe.db.sql(
				"delete from `tabSingles` where doctype=%s and field=%s", (doctype, old)
			)
		else:
			frappe.db.sql(
				"update `tabSingles` set field=%s where doctype=%s and field=%s",
				(new, doctype, old),
			)
