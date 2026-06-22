"""Aplica description em campos de DocType JSON do app Advocacia."""

from __future__ import annotations

import json
from pathlib import Path

SKIP_FIELDTYPES = frozenset({"Section Break", "Column Break", "Tab Break", "HTML", "Button"})

DESCRIPTIONS: dict[str, dict[str, str]] = {
	"Legal Case": {
		"client": "Client titular deste serviço ou processo.",
		"type": "Consultoria ou Processo Judicial. Define campos e validações do formulário.",
		"title": "Título automático no formato ID — cliente. Atualizado ao salvar.",
		"status": "Em andamento, Arquivado, Suspenso ou Encerrado.",
		"case_phase": "Fase atual do processo conforme cadastro rígido de Fases Processuais.",
		"opening_date": "Data de abertura do serviço ou distribuição do processo.",
		"case_number": "Número CNJ do processo (validado automaticamente). Obrigatório para Processo Judicial.",
		"legacy_numbering": "Número antigo ou interno, se diferente do CNJ.",
		"area": "Área do direito: Cível, Criminal, Trabalhista, etc.",
		"court_branch_link": "Court Branch judicial vinculada (cadastro rígido).",
		"court": "Court competente (cadastro rígido).",
		"jurisdiction": "Jurisdiction onde o processo tramita (cadastro rígido).",
		"opposing_party": "Nome da parte adversa, quando aplicável.",
		"case_value": "Valor atribuído à causa na petição inicial.",
		"remarks": "Anotações internas sobre o serviço ou processo.",
	},
	"Client": {
		"person_type": "Pessoa Física ou Pessoa Jurídica. Define quais documentos são obrigatórios.",
		"client_name": "Nome completo (PF) ou razão social (PJ). Aparece como título do registro.",
		"trade_name": "Nome fantasia da empresa (apenas pessoa jurídica).",
		"cpf": "CPF do cliente. Apenas dígitos, validado automaticamente.",
		"rg": "Documento de identidade (pessoa física).",
		"cnpj": "CNPJ do cliente. Apenas dígitos, validado automaticamente.",
		"nationality": "Nacionalidade do cliente (pessoa física).",
		"marital_status": "Estado civil (pessoa física).",
		"occupation": "Profissão declarada (pessoa física).",
		"representative": "Nome do representante legal (pessoa jurídica).",
		"representative_cpf": "CPF do representante legal, com validação automática.",
		"representative_role": "Cargo do representante legal na empresa.",
		"representative_nationality": "Nacionalidade do representante legal.",
		"contacts": "Telefones e e-mails de contato do cliente.",
		"addresses": "Endereços do cliente. Marque um como principal para documentos.",
		"remarks": "Anotações internas sobre o cliente.",
	},
	"Client Contact": {
		"contact_name": "Nome da pessoa de contato.",
		"type": "Relação com o cliente: Principal, Cônjuge, Responsável ou Outro.",
		"phone": "Telefone fixo com DDD (10 dígitos).",
		"mobile": "Celular com DDD (11 dígitos).",
		"email": "E-mail de contato. Armazenado em minúsculas.",
		"remarks": "Observações sobre este contato.",
	},
	"Client Address": {
		"type": "Finalidade: Residencial, Comercial, Correspondência ou Outro.",
		"cep": "CEP do endereço (apenas dígitos).",
		"street": "Rua, avenida ou equivalente.",
		"number": "Número do imóvel.",
		"complement": "Complemento (apto, sala, bloco).",
		"neighborhood": "Bairro.",
		"city": "Cidade.",
		"uf": "UF (sigla de dois caracteres).",
		"is_primary": "Marque o endereço principal usado em documentos gerados.",
	},
	"Legal Payment": {
		"title": "Título automático com ID e descritor.",
		"origin_type": "Honorários (Parcela) ou cobrança de serviço.",
		"fee_agreement": "Contrato de honorários que originou este recebimento (parcelas).",
		"service_record": "Cobrança de Serviço vinculada.",
		"legal_case": "Processo ou consultoria relacionado.",
		"client": "Preenchido automaticamente a partir do serviço ou honorários.",
		"installment_number": "Número sequencial da parcela no contrato de honorários.",
		"description": "Descrição exibida na parcela e nos relatórios.",
		"installment_origin_id": "Identificador interno para sincronização com parcelas de honorários.",
		"synced_at": "Data e hora da última sincronização automática.",
		"manual_override": "Quando marcado, o sistema não sobrescreve este pagamento na sincronização.",
		"amount": "Valor previsto da parcela ou cobrança.",
		"received_amount": "Valor efetivamente recebido.",
		"due_date": "Data de vencimento.",
		"received_date": "Data em que o pagamento foi recebido.",
		"status": "Pendente, Vencido, Recebido, Repassado, Cancelado ou Renegociado.",
		"remarks": "Observações internas sobre o pagamento.",
		"receipt": "Comprovante de recebimento anexado.",
	},
	"Fee Agreement": {
		"legal_case": "Processo ou consultoria vinculado ao contrato de honorários.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"fee_mode": "Honorários Diretos ou Divisão advogada/cliente (repasse ao cliente).",
		"status": "Vigente, Quitado ou Cancelado.",
		"total_agreement_value": "Valor total contratado entre as partes.",
		"lawyer_percentage": "Percentual da advogada sobre o total (modo divisão).",
		"fixed_fee_amount": "Valor fixo de honorários (modo misto).",
		"lawyer_amount": "Parcela destinada à advogada.",
		"billing_type": "Forma de cálculo: valor fixo, percentual ou misto.",
		"client_percentage": "Percentual do cliente sobre o total.",
		"client_amount": "Parcela destinada ao cliente (repasse).",
		"calculation_type": "Forma de cálculo da sucumbência: percentual ou valor fixo.",
		"contingency_fee_pct": "Percentual sobre a sucumbência.",
		"contingency_fee_amount": "Valor de honorários de sucumbência.",
		"contingency_fee_status": "Situação da sucumbência: pendente, recebida, etc.",
		"installment_count": "Quantidade de parcelas planejadas.",
		"first_installment_date": "Vencimento da primeira parcela.",
		"installment_amount": "Valor médio por parcela (referência).",
		"fee_installments": "Parcelas do contrato. Ao salvar, o sistema gera ou atualiza os pagamentos.",
		"lawyer_total": "Soma das parcelas da advogada. Calculado automaticamente.",
		"client_total": "Soma das parcelas do cliente. Calculado automaticamente.",
		"remarks": "Observações contratuais e anotações internas.",
		"title": "Título automático no formato ID — cliente.",
	},
	"Fee Installment": {
		"due_date": "Data de vencimento da parcela.",
		"total_amount": "Valor total da parcela.",
		"lawyer_amount": "Parte da parcela destinada à advogada.",
		"contingency_amount": "Parte referente à sucumbência.",
		"client_amount": "Parte repassada ao cliente.",
		"description": "Descrição exibida na parcela.",
		"installment_origin_id": "Identificador interno para sincronização. Gerado automaticamente.",
		"payment": "Recebimento vinculado gerado pela sincronização.",
		"status": "Pendente, Vencido, Recebido, Repassado ou Cancelado.",
		"received_date": "Data em que a parcela foi recebida.",
		"transfer_date": "Data do repasse ao cliente, quando aplicável.",
		"payment_method": "Forma de recebimento: PIX, TED, Dinheiro, etc.",
		"remarks": "Observações sobre esta parcela.",
	},
	"Hearing": {
		"legal_case": "Processo ou consultoria vinculado à audiência.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"hearing_datetime": "Data e hora da audiência.",
		"status": "Agendada, Realizada, Adiada ou Cancelada.",
		"type": "Tipo de audiência: Conciliação, Instrução, etc.",
		"modality": "Presencial, Virtual ou Híbrida.",
		"link_virtual": "Link de acesso para audiência virtual ou híbrida.",
		"court_branch": "Court Branch ou local da audiência (cadastro rígido).",
		"outcome": "Resultado ou desfecho da audiência.",
		"remarks": "Anotações sobre a audiência.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Deadline": {
		"legal_case": "Processo ou consultoria vinculado ao prazo.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"due_date": "Data fatal do prazo processual.",
		"status": "Pendente, Concluído ou Vencido. Vencido é atualizado automaticamente.",
		"description": "Descrição do compromisso ou prazo (ex.: contestação, recurso).",
		"priority": "Baixa, Média, Alta ou Urgente — usada em alertas e no painel.",
		"responsible": "Usuário responsável pelo cumprimento do prazo.",
		"notification_days": "Quantos dias antes do vencimento enviar alerta.",
		"remarks": "Observações adicionais sobre o prazo.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Legal Task": {
		"legal_case": "Processo relacionado (opcional).",
		"client": "Preenchido automaticamente a partir do serviço.",
		"subject": "Descrição curta da tarefa.",
		"status": "Pendente, Em Andamento, Concluída ou Cancelada.",
		"priority": "Baixa, Média ou Alta.",
		"due_date": "Prazo para conclusão da tarefa (opcional).",
		"description": "Detalhamento da tarefa e instruções.",
		"responsible": "Usuário responsável pela execução.",
		"completion_date": "Preenchida automaticamente ao concluir a tarefa.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Case Communication": {
		"legal_case": "Processo relacionado à comunicação (opcional).",
		"client": "Client envolvido na comunicação.",
		"communication_date": "Data e hora da comunicação.",
		"type": "Canal: Telefone, WhatsApp, E-mail, Reunião, etc.",
		"subject": "Assunto principal da comunicação.",
		"summary": "Resumo do que foi tratado.",
		"next_steps": "Próximos passos combinados (opcional).",
		"generate_task": "Marque para criar tarefa automaticamente a partir deste registro.",
		"legal_task": "Legal Task gerada a partir desta comunicação.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Service Record": {
		"legal_case": "Processo ou consultoria vinculado à cobrança.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"status": "Em aberto, Parcialmente cobrado ou Cobrado.",
		"opening_date": "Data de abertura da cobrança de serviços.",
		"acts": "Itens de serviço acumulados para cobrança.",
		"pending_total": "Soma dos itens pendentes. Calculado automaticamente.",
		"billed_total": "Soma dos itens já cobrados. Calculado automaticamente.",
		"grand_total": "Total geral dos itens. Calculado automaticamente.",
		"billing_due_date": "Vencimento sugerido ao sincronizar cobrança dos itens pendentes.",
		"last_payment": "Último pagamento vinculado a esta cobrança.",
		"remarks": "Observações sobre a cobrança de serviços.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Legal Act Item": {
		"act_date": "Data do serviço prestado.",
		"type": "Tipo do item: Inicial, Consulta, Audiência, etc.",
		"description": "Descrição do serviço prestado.",
		"amount": "Valor a cobrar por este item.",
		"status": "Pendente ou Cobrado.",
		"payment": "Recebimento vinculado quando o item foi faturado.",
	},
	"Time Entry": {
		"legal_case": "Processo onde a atividade foi realizada.",
		"client": "Preenchido automaticamente a partir do serviço.",
		"entry_date": "Data da atividade.",
		"activity": "Descrição curta da atividade realizada.",
		"category": "Categoria da atividade: Reunião, Petição, Pesquisa, etc.",
		"description": "Detalhamento complementar da atividade.",
		"billable": "Marque se o tempo deve entrar em relatórios de cobrança.",
		"duration_minutes": "Duração em minutos. Use o timer ou informe manualmente.",
		"duration_hours": "Duração convertida em horas. Calculada automaticamente.",
		"start_time": "Hora de início (timer).",
		"end_time": "Hora de término (timer).",
		"timer_active": "Indica se o timer está em execução.",
		"timer_start": "Momento em que o timer foi iniciado.",
		"responsible": "Profissional que registrou a atividade.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Court Cost": {
		"legal_case": "Processo ou consultoria vinculado à custa.",
		"description": "Descrição da custa ou taxa.",
		"type": "Taxa Judicial, Emolumento, Despesa Cartorial, etc.",
		"amount": "Valor da custa em reais.",
		"payment_date": "Data em que a custa foi paga.",
		"status": "Pendente, Pago, Repassado ou Cancelado.",
		"bill_to_client": "Marque se o valor deve ser repassado ao cliente.",
		"transfer_date": "Data do repasse ao cliente.",
		"payment_method": "Forma de pagamento: PIX, TED, Dinheiro, etc.",
		"receipt": "Comprovante de pagamento anexado.",
		"remarks": "Observações sobre a custa.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Office Expense": {
		"description": "Descrição da despesa (ex.: aluguel, internet).",
		"category": "Categoria: Aluguel, Salários, Software, etc.",
		"amount": "Valor da despesa em reais.",
		"due_date": "Data de vencimento.",
		"payment_date": "Data em que a despesa foi paga.",
		"status": "Pendente, Pago ou Atrasado.",
		"is_recurring": "Marque se a despesa se repete periodicamente.",
		"frequency": "Frequência da recorrência: Mensal, Anual, etc.",
		"next_due_date": "Próximo vencimento calculado (despesas recorrentes).",
		"payment_method": "Forma de pagamento: PIX, TED, Boleto, etc.",
		"receipt": "Comprovante de pagamento anexado.",
		"remarks": "Observações sobre a despesa.",
		"title": "Título automático no formato ID — descritor.",
	},
	"Jurisdiction": {
		"jurisdiction_name": "Nome único da comarca. Usado como identificador do registro.",
		"uf": "Unidade federativa (UF) da comarca.",
		"city": "Cidade sede da comarca.",
	},
	"Court Branch": {
		"court_branch_name": "Nome único da vara. Usado como identificador do registro.",
		"jurisdiction": "Jurisdiction à qual esta vara pertence.",
		"court_type": "Tipo: Cível, Criminal, Família, Trabalho, Federal ou Juizado Especial.",
	},
	"Court": {
		"court_name": "Nome único do tribunal.",
		"abbreviation": "Sigla oficial (ex.: TJRS, TRT4).",
		"jurisdiction": "Esfera: Estadual, Federal, Trabalho, Superior ou Militar.",
	},
	"Case Phase": {
		"case_phase_name": "Nome da fase (ex.: Conhecimento, Execução).",
		"sort_order": "Ordem de exibição no fluxo processual.",
	},
	"Document Template": {
		"title": "Nome do modelo. Identificador único no catálogo.",
		"document_type": "Tipo: Petição, Contrato, Procuração, etc.",
		"description": "Descrição do uso deste modelo.",
		"template_file": "Arquivo .docx com placeholders para geração.",
		"enabled": "Desmarque para ocultar o modelo na geração de documentos.",
		"show_placeholders": "Abre a referência de placeholders disponíveis no modelo.",
	},
	"Document Kit": {
		"title": "Nome do kit. Identificador único.",
		"description": "Descrição do conjunto de modelos incluídos.",
		"enabled": "Desmarque para desabilitar o kit na geração em lote.",
		"templates": "Modelos de documento incluídos neste kit.",
	},
	"Document Kit Item": {
		"template": "Modelo de documento incluído no kit.",
		"display_order": "Ordem de exibição e geração no kit.",
	},
	"Office Settings": {
		"company_name": "Razão social do escritório. Usada em documentos gerados.",
		"cnpj": "CNPJ do escritório. Usado em contratos e documentos oficiais.",
		"sia_registration": "Registro no SIA/OAB do escritório.",
		"office_logo": "Logotipo exibido em documentos gerados (opcional).",
		"lawyer_name": "Nome da advogada responsável pelo escritório.",
		"oab": "Número da OAB (apenas dígitos).",
		"default_notify_days": "Dias padrão de antecedência para alertas de prazos.",
		"address": "Endereço completo do escritório para documentos.",
		"bank_name": "Nome do banco para dados em contratos e recibos.",
		"bank_agency": "Agência bancária.",
		"bank_account": "Número da conta corrente.",
		"bank_pix": "Chave PIX para recebimentos.",
	},
}

FALLBACK_BY_FIELDTYPE: dict[str, str] = {
	"Link": "Selecione o registro vinculado.",
	"Select": "Escolha a opção adequada ao registro.",
	"Check": "Marque quando a condição se aplicar.",
	"Attach": "Anexe o arquivo correspondente.",
	"Attach Image": "Anexe a imagem correspondente.",
	"Table": "Preencha as linhas da tabela abaixo.",
	"Currency": "Valor em reais (R$).",
	"Percent": "Percentual de 0 a 100.",
	"Date": "Informe a data no formato DD/MM/AAAA.",
	"Datetime": "Informe data e hora.",
	"Int": "Número inteiro.",
	"Float": "Número decimal.",
	"Data": "Texto curto de identificação.",
	"Small Text": "Texto complementar.",
	"Text Editor": "Texto longo com formatação.",
}


def _permlevel_hint(permlevel: int) -> str:
	if permlevel and permlevel > 0:
		return " Visível apenas para Advocacia Manager."
	return ""


def _read_only_hint(read_only: int) -> str:
	if read_only:
		return " Preenchido ou calculado automaticamente pelo sistema."
	return ""


def apply_descriptions(doctype_json_path: Path) -> int:
	with open(doctype_json_path, encoding="utf-8") as f:
		data = json.load(f)

	if data.get("doctype") != "DocType":
		return 0

	doctype_name = data.get("name", "")
	field_map = DESCRIPTIONS.get(doctype_name, {})
	updated = 0

	for field in data.get("fields", []):
		ft = field.get("fieldtype")
		if ft in SKIP_FIELDTYPES:
			continue
		if field.get("description"):
			continue

		fn = field.get("fieldname", "")
		desc = field_map.get(fn)
		if not desc:
			base = FALLBACK_BY_FIELDTYPE.get(ft, "")
			if not base:
				continue
			desc = base
			desc += _read_only_hint(field.get("read_only", 0))
			desc += _permlevel_hint(field.get("permlevel", 0))
		else:
			pl = field.get("permlevel", 0)
			if pl and pl > 0 and "Advocacia Manager" not in desc:
				desc = desc.rstrip(".") + ". Visível apenas para Advocacia Manager."

		field["description"] = desc
		updated += 1

	if updated:
		with open(doctype_json_path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=1, ensure_ascii=False)
			f.write("\n")

	return updated


def run():
	"""Entry point for bench execute."""
	import frappe
	from frappe import _

	root = Path(frappe.get_app_path("advocacia")) / "advocacia" / "doctype"
	total = 0
	for path in sorted(root.glob("*/*.json")):
		count = apply_descriptions(path)
		if count:
			frappe.logger().info(f"{path.parent.name}: {count} fields")
			total += count
	frappe.msgprint(_("Descrições aplicadas em {0} campos.").format(total))
	return total


def main() -> None:
	root = Path(__file__).resolve().parents[1] / "doctype"
	total = 0
	for path in sorted(root.glob("*/*.json")):
		count = apply_descriptions(path)
		if count:
			print(f"{path.parent.name}: {count} fields")
			total += count
	print(f"Total: {total} descriptions added")


if __name__ == "__main__":
	main()
