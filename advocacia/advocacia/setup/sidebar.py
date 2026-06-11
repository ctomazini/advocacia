import os

import frappe

# Ordem canônica da sidebar Advocacia (espelha workspace_sidebar/advocacia.json).
# Seções: Dia a Dia | Gestão de Casos | Financeiro | Relatórios | Cadastros
SIDEBAR_LINK_ORDER = (
	# Dia a Dia
	("Painel", "painel", "Page"),
	("Prazos", "Deadline", "DocType"),
	("Audiências", "Hearing", "DocType"),
	("Tarefas", "Legal Task", "DocType"),
	("Comunicações", "Case Communication", "DocType"),
	# Gestão de Casos
	("Serviços", "Legal Case", "DocType"),
	("Clientes", "Client", "DocType"),
	("Registro de Horas", "Time Entry", "DocType"),
	("Registro de Atos", "Service Record", "DocType"),
	("Documentos do Processo", "Case Document", "DocType"),
	("Custas Processuais", "Court Cost", "DocType"),
	# Financeiro
	("Pagamentos", "Legal Payment", "DocType"),
	("Honorários", "Fee Agreement", "DocType"),
	("Despesas", "Office Expense", "DocType"),
	("Documentos", "Document Template", "DocType"),
	("Kits de Documentos", "Document Kit", "DocType"),
	# Relatórios
	("Produtividade", "produtividade", "Report"),
	("Horas por Serviço", "horas_por_servico", "Report"),
	("Inadimplência", "inadimplencia", "Report"),
	("Fluxo de Caixa", "fluxo_de_caixa", "Report"),
	("Honorários por Cliente", "honorarios_por_cliente", "Report"),
	("Carteira Ativa", "carteira_ativa", "Report"),
	# Cadastros
	("Comarca", "Jurisdiction", "DocType"),
	("Vara", "Court Branch", "DocType"),
	("Tribunal", "Court", "DocType"),
	("Fase Processual", "Case Phase", "DocType"),
	("Categoria de Documento", "Document Category", "DocType"),
	("Escritório", "Office Settings", "DocType"),
)

SIDEBAR_SECTIONS = (
	# Frappe v16: Section Break com filhos exige collapsible=1, senão toggle() quebra
	# ao fechar a sidebar (evento sidebar-expand) e o scroll do desk trava.
	{"label": "Dia a Dia", "collapsible": 1, "keep_closed": 0},
	{"label": "Gestão de Casos", "collapsible": 1, "keep_closed": 0},
	{"label": "Financeiro", "collapsible": 1, "keep_closed": 0},
	{"label": "Relatórios", "collapsible": 1, "keep_closed": 1},
	{"label": "Cadastros", "collapsible": 1, "keep_closed": 1},
)


def _validate_section_break_collapsible():
	"""Section Break com filhos deve ter collapsible=1 (requisito do Frappe v16 sidebar JS)."""
	if not frappe.db.exists("Workspace Sidebar", "Advocacia"):
		return

	sections = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Advocacia", "type": "Section Break"},
		fields=["label", "collapsible", "idx"],
		order_by="idx asc",
	)
	links = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Advocacia", "type": "Link"},
		fields=["idx"],
		order_by="idx asc",
	)
	link_idxs = [row.idx for row in links]

	for section in sections:
		has_children = any(idx > section.idx for idx in link_idxs)
		if has_children and not section.collapsible:
			frappe.log_error(
				title="Advocacia sidebar: Section Break sem collapsible",
				message=(
					f'Seção "{section.label}" tem itens filhos mas collapsible=0; '
					"isso quebra Sidebar.close() no desk (toggle sem $drop_icon)."
				),
			)


def _validate_sidebar_links():
	"""Garante que o JSON importado mantém os 26 links na ordem esperada."""
	if not frappe.db.exists("Workspace Sidebar", "Advocacia"):
		return

	links = frappe.get_all(
		"Workspace Sidebar Item",
		filters={"parent": "Advocacia", "type": "Link"},
		fields=["label", "link_to", "link_type", "idx"],
		order_by="idx asc",
	)

	if len(links) != len(SIDEBAR_LINK_ORDER):
		frappe.log_error(
			title="Advocacia sidebar: contagem de links divergente",
			message=f"Esperado {len(SIDEBAR_LINK_ORDER)}, encontrado {len(links)}",
		)
		return

	for idx, (expected, link) in enumerate(zip(SIDEBAR_LINK_ORDER, links, strict=True)):
		label, link_to, link_type = expected
		if (
			link.label != label
			or link.link_to != link_to
			or link.link_type != link_type
		):
			frappe.log_error(
				title="Advocacia sidebar: ordem divergente",
				message=(
					f"Posição {idx + 1}: esperado {label}/{link_to}/{link_type}, "
					f"encontrado {link.label}/{link.link_to}/{link.link_type}"
				),
			)
			return


def ensure_advocacia_sidebar():
	"""Garante Workspace Sidebar e Desktop Icon do app (sync idempotente)."""
	for folder, filename in (
		("workspace_sidebar", "advocacia.json"),
		("desktop_icon", "advocacia.json"),
	):
		path = frappe.get_app_path("advocacia", folder, filename)
		if os.path.exists(path):
			frappe.import_doc(path)

	_validate_sidebar_links()
	_validate_section_break_collapsible()
	frappe.clear_cache()
	frappe.db.commit()
