/* ═══════════════════════════════════════════════════════════
   adv_hub — Render functions for Legal Case hub tabs
   ═══════════════════════════════════════════════════════════ */

window.advocacia = window.advocacia || {};

function _nav_label(doctype) {
	return adv_case_nav.get_doctype_label(doctype);
}

function adv_hub_load(frm) {
	if (frm.is_new()) {
		return;
	}

	frappe.call({
		method: "advocacia.advocacia.case_hub.get_case_counts",
		args: { case: frm.doc.name },
		callback(r) {
			adv_hub_render_summary_bar(frm, r.message || {});
		},
	});

	frappe.call({
		method: "advocacia.advocacia.case_hub.get_case_hub_data",
		args: { case: frm.doc.name },
		callback(r) {
			const data = r.message || {};
			adv_hub_render_phases(frm, data.phases || []);
			adv_hub_render_hearings(frm, data.hearings || []);
			adv_hub_render_deadlines(frm, data.deadlines || []);
			adv_hub_render_tasks(frm, data.tasks || []);
			adv_hub_render_communications(frm, data.communications || []);
			adv_hub_render_service_records(frm, data.service_records || []);
			adv_hub_render_time_entries(frm, data.time_entries || {});
			adv_hub_render_documents(frm, data.documents || []);
			adv_hub_render_document_kits(frm, data.document_kits || []);
			adv_hub_render_financial(frm, data.financial);
		},
	});
}

advocacia.hub = { load: adv_hub_load };

function adv_hub_render_phases(frm, phases) {
	const $w = frm.fields_dict.phases_panel?.$wrapper;
	if (!$w) return;

	if (!phases.length) {
		$w.html(`<div class="adv-hub-panel">
			<div class="adv-hub-empty">
				<div class="adv-hub-empty__icon">📋</div>
				<div>${__("Nenhuma fase processual definida.")}</div>
				<p class="text-muted small">${__(
					"Selecione a fase atual no campo Fase Processual acima."
				)}</p>
			</div>
		</div>`);
		return;
	}

	const phase = phases[0];
	const label = phase.case_phase_name || phase.name;
	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-phase-current">
			<span class="adv-hub-phase-current__icon">📋</span>
			<span>${__("Fase atual")}: <strong>${frappe.utils.escape_html(label)}</strong></span>
		</div>
	</div>`);
}

function adv_hub_render_hearings(frm, hearings) {
	const $w = frm.fields_dict.hearings_panel?.$wrapper;
	if (!$w) return;

	if (!hearings.length) {
		$w.html(
			_adv_hub_empty(
				"⚖️",
				__("Nenhuma audiência agendada para este processo."),
				"",
				__("+ Audiência"),
				"new-hearing"
			)
		);
		$w.find('[data-hub-action="new-hearing"]').on("click", () => {
			adv_case_nav_new_doc("Hearing", {
				legal_case: frm.doc.name,
				client: frm.doc.client,
			});
		});
		return;
	}

	const items = hearings
		.map((row) => {
			const dt = row.hearing_datetime
				? frappe.datetime.str_to_user(row.hearing_datetime)
				: "—";
			const meta = [row.type, row.modality].filter(Boolean).join(" · ");
			return `<div class="adv-hub-timeline-item" data-route="Form/Hearing/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-timeline-dot adv-hub-timeline-dot--${row.urgency || "normal"}"></div>
			<div style="flex:1">
				<div class="adv-hub-timeline-title">${frappe.utils.escape_html(
					row.title || row.name
				)}</div>
				<div class="adv-hub-timeline-meta">
					<span>${dt}</span>
					${meta ? `<span>·</span><span>${frappe.utils.escape_html(meta)}</span>` : ""}
				</div>
			</div>
			${_adv_hub_status_badge(row.status)}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">⚖️</span>
				${_nav_label("Hearing")}
				<span class="adv-hub-panel__count">${hearings.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-hearing">
				${__("+ Audiência")}
			</button>
		</div>
		${items}
	</div>`);

	$w.find('[data-hub-action="new-hearing"]').on("click", () => {
		adv_case_nav_new_doc("Hearing", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_deadlines(frm, deadlines) {
	const $w = frm.fields_dict.deadlines_panel?.$wrapper;
	if (!$w) return;

	if (!deadlines.length) {
		$w.html(
			_adv_hub_empty(
				"📅",
				__("Nenhum prazo registrado."),
				__("Cadastre prazos processuais com data fatal."),
				__("+ Prazo"),
				"new-deadline"
			)
		);
		$w.find('[data-hub-action="new-deadline"]').on("click", () => {
			adv_case_nav_new_doc("Deadline", { legal_case: frm.doc.name, client: frm.doc.client });
		});
		return;
	}

	const items = deadlines
		.map((row) => {
			const dt = row.due_date ? frappe.datetime.str_to_user(row.due_date) : "—";
			let daysHtml = "";
			if (row.days_remaining !== null && row.urgency !== "done") {
				if (row.days_remaining < 0) {
					daysHtml = `<span style="color:var(--red-500);font-weight:600">${Math.abs(
						row.days_remaining
					)}d ${__("atrasado")}</span>`;
				} else if (row.days_remaining === 0) {
					daysHtml = `<span style="color:var(--orange-500);font-weight:600">${__(
						"Vence hoje!"
					)}</span>`;
				} else {
					daysHtml = `<span>${row.days_remaining}d</span>`;
				}
			}
			return `<div class="adv-hub-timeline-item" data-route="Form/Deadline/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-timeline-dot adv-hub-timeline-dot--${row.urgency}"></div>
			<div style="flex:1">
				<div class="adv-hub-timeline-title">${frappe.utils.escape_html(
					row.title || row.name
				)}</div>
				<div class="adv-hub-timeline-meta">
					<span>${dt}</span>
					${daysHtml ? "<span>·</span>" + daysHtml : ""}
					${
						row.priority
							? `<span>·</span><span>${frappe.utils.escape_html(row.priority)}</span>`
							: ""
					}
				</div>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">📅</span>
				${_nav_label("Deadline")}
				<span class="adv-hub-panel__count">${deadlines.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-deadline">
				${__("+ Prazo")}
			</button>
		</div>
		${items}
	</div>`);

	$w.find('[data-hub-action="new-deadline"]').on("click", () => {
		adv_case_nav_new_doc("Deadline", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_tasks(frm, tasks) {
	const $w = frm.fields_dict.tasks_panel?.$wrapper;
	if (!$w) return;

	if (!tasks.length) {
		$w.html(
			_adv_hub_empty(
				"✅",
				__("Nenhuma tarefa interna para este processo."),
				"",
				__("+ Tarefa"),
				"new-task"
			)
		);
		$w.find('[data-hub-action="new-task"]').on("click", () => {
			adv_case_nav_new_doc("Legal Task", { legal_case: frm.doc.name, client: frm.doc.client });
		});
		return;
	}

	const rows = tasks
		.map((row) => {
			const dt = row.due_date ? frappe.datetime.str_to_user(row.due_date) : "—";
			return `<div class="adv-hub-list-row" data-route="Form/Legal Task/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(row.subject || row.name)}
				<span class="adv-hub-list-row__secondary">${dt}</span>
			</div>
			${_adv_hub_status_badge(row.status)}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">✅</span>
				${_nav_label("Legal Task")}
				<span class="adv-hub-panel__count">${tasks.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-task">
				${__("+ Tarefa")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-task"]').on("click", () => {
		adv_case_nav_new_doc("Legal Task", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_communications(frm, communications) {
	const $w = frm.fields_dict.communications_panel?.$wrapper;
	if (!$w) return;

	if (!communications.length) {
		$w.html(
			_adv_hub_empty(
				"💬",
				__("Nenhuma comunicação registrada."),
				"",
				__("+ Comunicação"),
				"new-comm"
			)
		);
		$w.find('[data-hub-action="new-comm"]').on("click", () => {
			adv_case_nav_new_doc("Case Communication", {
				legal_case: frm.doc.name,
				client: frm.doc.client,
			});
		});
		return;
	}

	const rows = communications
		.map((row) => {
			const dt = row.communication_date
				? frappe.datetime.str_to_user(row.communication_date)
				: "—";
			return `<div class="adv-hub-list-row" data-route="Form/Case Communication/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(row.title || row.subject || row.name)}
				<span class="adv-hub-list-row__secondary">${dt}${
					row.type ? " · " + frappe.utils.escape_html(row.type) : ""
				}</span>
			</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">💬</span>
				${_nav_label("Case Communication")}
				<span class="adv-hub-panel__count">${communications.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-comm">
				${__("+ Comunicação")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-comm"]').on("click", () => {
		adv_case_nav_new_doc("Case Communication", {
			legal_case: frm.doc.name,
			client: frm.doc.client,
		});
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_service_records(frm, records) {
	const $w = frm.fields_dict.service_records_panel?.$wrapper;
	if (!$w) return;

	if (!records.length) {
		$w.html(
			_adv_hub_empty(
				"📝",
				__("Nenhuma cobrança individual registrada."),
				__(
					"Use Cobranças Individuais para registrar atos cobrados fora da cobrança de honorários."
				),
				__("+ Cobrança Individual"),
				"new-record"
			)
		);
		$w.find('[data-hub-action="new-record"]').on("click", () => {
			adv_case_nav_new_doc("Service Record", { legal_case: frm.doc.name, client: frm.doc.client });
		});
		return;
	}

	const rows = records
		.map((row) => {
			return `<div class="adv-hub-list-row" data-route="Form/Service Record/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(row.title || row.name)}
				<span class="adv-hub-list-row__secondary">${__(
					"{0} item(ns)",
					[row.act_count || 0]
				)} · ${format_currency(row.grand_total || 0)}</span>
			</div>
			${_adv_hub_status_badge(row.status)}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">📝</span>
				${_nav_label("Service Record")}
				<span class="adv-hub-panel__count">${records.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-record">
				${__("+ Cobrança Individual")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-record"]').on("click", () => {
		adv_case_nav_new_doc("Service Record", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_time_entries(frm, payload) {
	const $w = frm.fields_dict.time_entries_panel?.$wrapper;
	if (!$w) return;

	const items = payload.items || [];
	const totalHours = payload.total_hours || 0;

	if (!items.length) {
		$w.html(
			_adv_hub_empty(
				"⏱️",
				__("Nenhum registro de horas."),
				"",
				__("+ Registro de Horas"),
				"new-time"
			)
		);
		$w.find('[data-hub-action="new-time"]').on("click", () => {
			adv_case_nav_new_doc("Time Entry", { legal_case: frm.doc.name, client: frm.doc.client });
		});
		return;
	}

	const rows = items
		.map((row) => {
			const dt = row.entry_date ? frappe.datetime.str_to_user(row.entry_date) : "—";
			return `<div class="adv-hub-list-row" data-route="Form/Time Entry/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(row.activity || row.title || row.name)}
				<span class="adv-hub-list-row__secondary">${dt}</span>
			</div>
			<div class="adv-hub-list-row__value">${row.hours || 0}h</div>
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">⏱️</span>
				${_nav_label("Time Entry")}
				<span class="adv-hub-panel__count">${items.length}</span>
			</h3>
			<div class="adv-hub-panel__actions">
				<span class="text-muted small">${__("Total")}: <strong>${totalHours}h</strong></span>
				<button type="button" class="adv-hub-panel__action" data-hub-action="new-time">
					${__("+ Registro de Horas")}
				</button>
			</div>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-time"]').on("click", () => {
		adv_case_nav_new_doc("Time Entry", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_documents(frm, documents) {
	const $w = frm.fields_dict.documents_panel?.$wrapper;
	if (!$w) return;

	const headerActions = `<div class="adv-hub-panel__actions">
		<button type="button" class="adv-hub-panel__action" data-hub-action="new-document">
			${__("+ Enviar")}
		</button>
		<button type="button" class="adv-hub-panel__action" data-hub-action="generate-docs">
			${__("Gerar .docx")}
		</button>
	</div>`;

	if (!documents.length) {
		$w.html(`<div class="adv-hub-panel">
			<div class="adv-hub-panel__header">
				<h3 class="adv-hub-panel__title">
					<span class="adv-hub-panel__title-icon">📄</span>
				${_nav_label("Case Document")}
					<span class="adv-hub-panel__count">0</span>
				</h3>
				${headerActions}
			</div>
			<div class="adv-hub-empty">
				<div class="adv-hub-empty__icon">📄</div>
				<p class="adv-hub-empty__title">${__("Nenhum documento anexado.")}</p>
				<p class="adv-hub-empty__hint">${__(
					"Use o botão + para fazer upload ou Gerar Documentos para criar a partir de modelos Word."
				)}</p>
				<button type="button" class="adv-hub-empty__action" data-hub-action="new-document">
					${__("+ Documento")}
				</button>
			</div>
		</div>`);
		_adv_hub_bind_document_actions(frm, $w);
		return;
	}

	const statusMap = {
		Rascunho: "gray",
		Assinado: "blue",
		Protocolado: "orange",
		Juntado: "green",
		Substituído: "gray",
	};
	const sourceIcons = {
		"Gerado pelo App": "⚙️",
		"Upload Manual": "📤",
		Digitalizado: "🖨️",
	};

	const rows = documents
		.map((doc) => {
			const badge = `<span class="adv-hub-badge adv-hub-badge--${
				statusMap[doc.status] || "gray"
			}">${frappe.utils.escape_html(doc.status || "")}</span>`;
			const sourceIcon = sourceIcons[doc.source] || "📄";
			const version = doc.version_label
				? `<span class="adv-hub-list-row__secondary">${frappe.utils.escape_html(
						doc.version_label
				  )}</span>`
				: "";
			const fileLink = doc.file
				? `<a href="${frappe.utils.escape_html(
						doc.file
				  )}" target="_blank" class="adv-hub-doc-file" title="${__("Abrir arquivo")}">📎</a>`
				: "";
			return `<div class="adv-hub-list-row" data-route="Form/Case Document/${frappe.utils.escape_html(
				doc.name
			)}">
			<div class="adv-hub-list-row__icon">${sourceIcon}</div>
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(doc.title || doc.name)}
				<span class="adv-hub-list-row__secondary">${frappe.utils.escape_html(
					doc.category || ""
				)}</span>
				${version}
			</div>
			${fileLink}
			${badge}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">📄</span>
				${_nav_label("Case Document")}
				<span class="adv-hub-panel__count">${documents.length}</span>
			</h3>
			${headerActions}
		</div>
		${rows}
	</div>`);

	_adv_hub_bind_document_actions(frm, $w);
	_adv_hub_bind_routes($w);
	$w.find(".adv-hub-doc-file").on("click", (event) => {
		event.stopPropagation();
	});
}

function _adv_hub_bind_document_actions(frm, $w) {
	$w.find('[data-hub-action="new-document"]').on("click", () => {
		adv_case_nav_new_doc("Case Document", {
			legal_case: frm.doc.name,
			client: frm.doc.client,
		});
	});
	$w.find('[data-hub-action="generate-docs"]').on("click", () => {
		if (window.advocacia?.openGenerateDocumentsDialog) {
			advocacia.openGenerateDocumentsDialog(frm);
		}
	});
}

function adv_hub_render_document_kits(frm, kits) {
	const $w = frm.fields_dict.document_kits_panel?.$wrapper;
	if (!$w) return;

	const cards = (kits || [])
		.map(
			(kit) => `<div class="adv-hub-kit-card" data-kit="${frappe.utils.escape_html(kit.name)}">
			<div class="adv-hub-kit-card__title">${frappe.utils.escape_html(kit.title || kit.name)}</div>
			${
				kit.description
					? `<div class="adv-hub-kit-card__desc">${frappe.utils.escape_html(
							kit.description
					  )}</div>`
					: ""
			}
		</div>`
		)
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">📦</span>
				${_nav_label("Document Kit")}
				<span class="adv-hub-panel__count">${(kits || []).length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="generate-docs">
				${__("Gerar Documentos")}
			</button>
		</div>
		${
			cards ||
			`<div class="adv-hub-empty"><div>${__(
				"Nenhum kit de documentos habilitado."
			)}</div></div>`
		}
	</div>`);

	$w.find('[data-hub-action="generate-docs"]').on("click", () => {
		if (window.advocacia?.openGenerateDocumentsDialog) {
			advocacia.openGenerateDocumentsDialog(frm);
		}
	});
	$w.find(".adv-hub-kit-card").on("click", () => {
		if (window.advocacia?.openGenerateDocumentsDialog) {
			advocacia.openGenerateDocumentsDialog(frm);
		}
	});
}

function adv_hub_render_financial(frm, financial) {
	const panels = [
		"financial_summary_panel",
		"installments_panel",
		"payments_panel",
		"court_costs_panel",
	];

	if (!financial) {
		const $summary = frm.fields_dict.financial_summary_panel?.$wrapper;
		if ($summary) {
			$summary.html(`<div class="adv-hub-budget-banner adv-hub-budget-banner--info">
				<div class="adv-hub-budget-banner__head">
					<strong>${__("Dados financeiros restritos")}</strong>
				</div>
				<p class="adv-hub-budget-banner__hint">${__(
					"Área restrita ao perfil Gestor. Solicite acesso ao administrador se necessário."
				)}</p>
			</div>`);
		}
		panels.slice(1).forEach((panel) => {
			if (frm.fields_dict[panel]) {
				frm.fields_dict[panel].$wrapper.html("");
			}
		});
		return;
	}

	_adv_hub_render_financial_summary(frm, financial);
	_adv_hub_render_installments(frm, financial.installments || []);
	_adv_hub_render_payments(frm, financial.payments || []);
	_adv_hub_render_court_costs(frm, financial.court_costs || []);
}

function _adv_hub_finance_narrative_banner() {
	return `<div class="adv-hub-budget-banner adv-hub-budget-banner--info adv-hub-finance-narrative">
		<p>${__("O financeiro do processo tem duas fontes de receita:")}</p>
		<ul class="adv-hub-finance-narrative__list">
			<li><strong>${__("Cobranças de Honorários")}</strong> — ${__(
				"valor acordado na Cobrança de Honorários, dividido em parcelas geradas automaticamente."
			)}</li>
			<li><strong>${__("Cobranças Individuais")}</strong> — ${__(
				"atos cobrados fora da cobrança de honorários."
			)}</li>
		</ul>
		<p>${__(
			"Ambos geram Recebimentos para controle. Custas Processuais (taxas, perícias) são despesas do processo, não receita."
		)}</p>
	</div>`;
}

function _adv_hub_render_financial_summary(frm, financial) {
	const $w = frm.fields_dict.financial_summary_panel?.$wrapper;
	if (!$w) return;

	const summary = financial.summary || {};
	const agreement = financial.agreement;
	const pctReceived = summary.total_contract
		? Math.min(100, Math.round((summary.total_received / summary.total_contract) * 100))
		: 0;

	const pendingBillings = (financial.service_billings || []).filter(
		(row) => flt(row.pending_total) > 0
	);
	const billingRows = pendingBillings
		.map((row) => {
			return `<div class="adv-hub-list-row" data-route="Form/Service Record/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(row.title || row.name)}
				<span class="adv-hub-list-row__secondary">${format_currency(row.pending_total)} ${__(
					"a faturar"
				)}</span>
			</div>
			${_adv_hub_status_badge(row.status)}
		</div>`;
		})
		.join("");
	const billingSection = pendingBillings.length
		? `<div class="adv-hub-subsection">
			<div class="adv-hub-subsection__header">
				<strong>${__("Cobranças individuais em aberto")}</strong>
				<button type="button" class="adv-hub-panel__action" data-hub-action="list-service-records">${__(
					"Ver todas"
				)}</button>
			</div>
			${billingRows}
		</div>`
		: "";

	$w.html(`<div class="adv-hub-panel">
		${_adv_hub_finance_narrative_banner()}
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">💰</span>
				${__("Resumo Financeiro")}
			</h3>
			${
				agreement
					? `<button type="button" class="adv-hub-panel__action" data-route="Form/Fee Agreement/${frappe.utils.escape_html(
							agreement.name
					  )}">${__("Ver Cobrança de Honorários")}</button>`
					: `<button type="button" class="adv-hub-panel__action" data-hub-action="new-agreement">${__(
							"+ Cobrança de Honorários"
					  )}</button>`
			}
		</div>
		<p class="adv-hub-panel__hint">${__(
			"Cobranças de honorários: valor parcelado do caso. Cobranças individuais: itens a faturar ou já emitidos em recebimento."
		)}</p>
		<div class="adv-hub-kpi-row">
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--blue-500)">${format_currency(
					summary.total_contract
				)}</div>
				<div class="adv-hub-kpi__label">${__("Cobrança de honorários")}</div>
			</div>
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--green-600)">${format_currency(
					summary.total_received
				)}</div>
				<div class="adv-hub-kpi__label">${__("Recebido")}</div>
			</div>
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--orange-500)">${format_currency(
					summary.total_pending_honorarios
				)}</div>
				<div class="adv-hub-kpi__label">${__("Recebimentos pendentes")}</div>
			</div>
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--purple-500)">${format_currency(
					summary.total_services_unbilled
				)}</div>
				<div class="adv-hub-kpi__label">${__("A faturar (individuais)")}</div>
			</div>
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--red-500)">${format_currency(
					summary.total_costs
				)}</div>
				<div class="adv-hub-kpi__label">${_nav_label("Court Cost")}</div>
			</div>
		</div>
		${
			summary.total_pending_service_payments
				? `<p class="adv-hub-panel__hint">${__(
						"Cobranças individuais já emitidas e aguardando recebimento: {0}",
						[format_currency(summary.total_pending_service_payments)]
				  )}</p>`
				: ""
		}
		<div class="adv-hub-stacked-bar" title="${__("{0}% recebido da cobrança de honorários", [pctReceived])}">
			<div class="adv-hub-stacked-bar__segment" style="width:${pctReceived}%;background:var(--green-500)"></div>
		</div>
		${billingSection}
	</div>`);

	$w.find("[data-route]").on("click", function () {
		adv_case_nav_follow_route($(this).attr("data-route"));
	});
	$w.find('[data-hub-action="new-agreement"]').on("click", () => {
		adv_case_nav_new_doc("Fee Agreement", {
			legal_case: frm.doc.name,
			client: frm.doc.client,
		});
	});
	$w.find('[data-hub-action="list-service-records"]').on("click", () => {
		adv_case_nav_set_route("List", "Service Record", { legal_case: frm.doc.name });
	});
}

function _adv_hub_render_installments(frm, installments) {
	const $w = frm.fields_dict.installments_panel?.$wrapper;
	if (!$w) return;

	if (!installments.length) {
		$w.html(
			_adv_hub_empty(
				"📋",
				__("Nenhum recebimento de honorários registrado."),
				__(
					"Para gerar parcelas, cadastre uma Cobrança de Honorários para este processo."
				),
				__("+ Cobrança de Honorários"),
				"new-agreement"
			)
		);
		$w.find('[data-hub-action="new-agreement"]').on("click", () => {
			adv_case_nav_new_doc("Fee Agreement", {
				legal_case: frm.doc.name,
				client: frm.doc.client,
			});
		});
		return;
	}

	const rows = installments
		.map((row) => {
			const dt = row.due_date ? frappe.datetime.str_to_user(row.due_date) : "—";
			return `<div class="adv-hub-list-row" data-route="Form/Fee Agreement/${frappe.utils.escape_html(
				row.fee_agreement
			)}">
			<div class="adv-hub-list-row__main">
				<span style="color:var(--text-muted);margin-right:4px">#${row.idx || ""}</span>
				${dt}
				<span class="adv-hub-list-row__secondary">${frappe.utils.escape_html(
					row.fee_agreement_title || ""
				)}</span>
			</div>
			<div class="adv-hub-list-row__value">${format_currency(row.total_amount)}</div>
			${_adv_hub_status_badge(row.status)}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">📋</span>
				${_nav_label("Fee Installment")}
				<span class="adv-hub-panel__count">${installments.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="list-agreements">
				${__("Ver Cobrança de Honorários")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="list-agreements"]').on("click", () => {
		adv_case_nav_set_route("List", "Fee Agreement", { legal_case: frm.doc.name });
	});
	_adv_hub_bind_routes($w);
}

function _adv_hub_render_payments(frm, payments) {
	const $w = frm.fields_dict.payments_panel?.$wrapper;
	if (!$w) return;

	if (!payments.length) {
		$w.html(
			_adv_hub_empty(
				"💵",
				__("Nenhum recebimento registrado."),
				__(
					"Para gerar parcelas, cadastre uma Cobrança de Honorários para este processo."
				),
				__("+ Cobrança de Honorários"),
				"new-agreement"
			)
		);
		$w.find('[data-hub-action="new-agreement"]').on("click", () => {
			adv_case_nav_new_doc("Fee Agreement", {
				legal_case: frm.doc.name,
				client: frm.doc.client,
			});
		});
		return;
	}

	const rows = payments
		.map((row) => {
			const dt = row.due_date ? frappe.datetime.str_to_user(row.due_date) : "—";
			return `<div class="adv-hub-list-row" data-route="Form/Legal Payment/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(row.title || row.name)}
				<span class="adv-hub-list-row__secondary">${dt}</span>
			</div>
			<div class="adv-hub-list-row__value">${format_currency(row.amount)}</div>
			${_adv_hub_status_badge(row.status)}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">💵</span>
				${_nav_label("Legal Payment")}
				<span class="adv-hub-panel__count">${payments.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-payment">
				${`+ ${_nav_label("Legal Payment")}`}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-payment"]').on("click", () => {
		adv_case_nav_new_doc("Legal Payment", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function _adv_hub_render_court_costs(frm, costs) {
	const $w = frm.fields_dict.court_costs_panel?.$wrapper;
	if (!$w) return;

	if (!costs.length) {
		$w.html(
			_adv_hub_empty(
				"🏛️",
				__("Nenhuma custa registrada."),
				__("Registre taxas judiciais, perícias e emolumentos pagos."),
				__("+ Custa Processual"),
				"new-cost"
			)
		);
		$w.find('[data-hub-action="new-cost"]').on("click", () => {
			adv_case_nav_new_doc("Court Cost", { legal_case: frm.doc.name, client: frm.doc.client });
		});
		return;
	}

	const rows = costs
		.map((row) => {
			const dt = row.payment_date ? frappe.datetime.str_to_user(row.payment_date) : "—";
			return `<div class="adv-hub-list-row" data-route="Form/Court Cost/${frappe.utils.escape_html(
				row.name
			)}">
			<div class="adv-hub-list-row__main">
				${frappe.utils.escape_html(row.title || row.description || row.name)}
				<span class="adv-hub-list-row__secondary">${dt}${
					row.type ? " · " + frappe.utils.escape_html(row.type) : ""
				}</span>
			</div>
			<div class="adv-hub-list-row__value">${format_currency(row.amount)}</div>
			${_adv_hub_status_badge(row.status)}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">🏛️</span>
				${_nav_label("Court Cost")}
				<span class="adv-hub-panel__count">${costs.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-cost">
				${`+ ${_nav_label("Court Cost")}`}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-cost"]').on("click", () => {
		adv_case_nav_new_doc("Court Cost", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function _adv_hub_render_case_checklist(frm, counts) {
	const isJudicial = frm.doc.type === "Processo Judicial";
	const items = [];

	if ("fee_agreements" in counts) {
		items.push({
			label: __("Cobrança de Honorários cadastrada"),
			done: (counts.fee_agreements || 0) > 0,
			doctype: "Fee Agreement",
			fieldname: "legal_case",
		});
	}
	items.push({
		label: __("Pelo menos um Prazo registrado"),
		done: (counts.deadlines || 0) > 0,
		doctype: "Deadline",
		fieldname: "legal_case",
	});
	if (isJudicial) {
		items.push({
			label: __("Pelo menos uma Audiência"),
			done: (counts.hearings || 0) > 0,
			doctype: "Hearing",
			fieldname: "legal_case",
		});
	}

	if (!items.some((item) => !item.done)) {
		return "";
	}

	const rows = items
		.map((item) => {
			const mark = item.done ? "☑" : "☐";
			const cls = item.done ? " adv-hub-checklist__item--done" : "";
			const cta = item.done
				? ""
				: `<button type="button" class="adv-hub-checklist__add" data-doctype="${frappe.utils.escape_html(
						item.doctype
				  )}" data-fieldname="${frappe.utils.escape_html(item.fieldname)}">+</button>`;
			return `<li class="adv-hub-checklist__item${cls}">
				<span class="adv-hub-checklist__mark">${mark}</span>
				<span class="adv-hub-checklist__label">${frappe.utils.escape_html(item.label)}</span>
				${cta}
			</li>`;
		})
		.join("");

	return `<div class="adv-hub-checklist">
		<p class="adv-hub-checklist__title">${__("Checklist do processo")}</p>
		<ul class="adv-hub-checklist__list">${rows}</ul>
	</div>`;
}

function adv_hub_render_summary_bar(frm, counts) {
	const $w = frm.fields_dict.hub_summary_bar?.$wrapper;
	if (!$w) return;

	const caseName = frm.doc.name;
	const items = [
		{
			icon: "⚖️",
			label: _nav_label("Hearing"),
			count: counts.hearings,
			doctype: "Hearing",
			fieldname: "legal_case",
		},
		{
			icon: "📅",
			label: _nav_label("Deadline"),
			count: counts.deadlines,
			doctype: "Deadline",
			fieldname: "legal_case",
		},
		{
			icon: "✅",
			label: _nav_label("Legal Task"),
			count: counts.tasks,
			doctype: "Legal Task",
			fieldname: "legal_case",
		},
		{
			icon: "💬",
			label: _nav_label("Case Communication"),
			count: counts.communications,
			doctype: "Case Communication",
			fieldname: "legal_case",
		},
		{
			icon: "⏱️",
			label: _nav_label("Time Entry"),
			count: counts.time_entries,
			doctype: "Time Entry",
			fieldname: "legal_case",
		},
		{
			icon: "📄",
			label: _nav_label("Case Document"),
			count: counts.documents,
			doctype: "Case Document",
			fieldname: "legal_case",
		},
		{
			icon: "📦",
			label: _nav_label("Document Kit"),
			count: counts.document_kits,
			doctype: "Document Kit",
			fieldname: null,
			catalog: true,
		},
	];

	if ("fee_agreements" in counts) {
		items.push(
			{
				icon: "📑",
				label: _nav_label("Fee Agreement"),
				count: counts.fee_agreements,
				doctype: "Fee Agreement",
				fieldname: "legal_case",
			},
			{
				icon: "💵",
				label: _nav_label("Legal Payment"),
				count: counts.payments,
				doctype: "Legal Payment",
				fieldname: "legal_case",
			},
			{
				icon: "📝",
				label: _nav_label("Service Record"),
				count: counts.service_records,
				doctype: "Service Record",
				fieldname: "legal_case",
			},
			{
				icon: "🏛️",
				label: _nav_label("Court Cost"),
				count: counts.court_costs,
				doctype: "Court Cost",
				fieldname: "legal_case",
			}
		);
	} else {
		items.push({
			icon: "📝",
			label: _nav_label("Service Record"),
			count: counts.service_records,
			doctype: "Service Record",
			fieldname: "legal_case",
		});
	}

	const pills = items
		.map((item) => {
			const hasData = (item.count || 0) > 0;
			const filterValue = item.catalog ? null : caseName;
			const listUrl = item.fieldname
				? `/app/${frappe.router.slug(item.doctype)}?${item.fieldname}=${encodeURIComponent(
						filterValue
				  )}`
				: `/app/${frappe.router.slug(item.doctype)}`;

			return `<div class="adv-hub-summary-pill${
				hasData ? " adv-hub-summary-pill--active" : ""
			}">
			<a class="adv-hub-summary-pill__link" href="${listUrl}"
				data-doctype="${frappe.utils.escape_html(item.doctype)}"
				data-fieldname="${frappe.utils.escape_html(item.fieldname || "")}"
				data-catalog="${item.catalog ? "1" : "0"}"
				title="${frappe.utils.escape_html(__("Ver lista de {0}", [item.label]))}">
				<span class="adv-hub-summary-pill__icon">${item.icon}</span>
				<span class="adv-hub-summary-pill__label">${item.label}</span>
				<span class="adv-hub-summary-pill__count">${item.count || 0}</span>
			</a>
			${
				item.readonly
					? ""
					: `<button type="button" class="adv-hub-summary-pill__add"
				data-doctype="${frappe.utils.escape_html(item.doctype)}"
				data-fieldname="${frappe.utils.escape_html(item.fieldname || "")}"
				title="${frappe.utils.escape_html(__("Criar {0}", [item.label]))}">+</button>`
			}
		</div>`;
		})
		.join("");

	const checklistHtml = _adv_hub_render_case_checklist(frm, counts);
	$w.html(`${checklistHtml}<div class="adv-hub-summary-bar">${pills}</div>`);

	$w.find(".adv-hub-checklist__add").on("click", function (e) {
		e.preventDefault();
		const doctype = $(this).attr("data-doctype");
		const fieldname = $(this).attr("data-fieldname");
		const defaults = {};
		if (fieldname) {
			defaults[fieldname] = caseName;
			if (frm.doc.client) {
				defaults.client = frm.doc.client;
			}
		}
		adv_case_nav_new_doc(doctype, defaults);
	});

	$w.find(".adv-hub-summary-pill__link").on("click", function (e) {
		e.preventDefault();
		const doctype = $(this).attr("data-doctype");
		const fieldname = $(this).attr("data-fieldname");
		const isCatalog = $(this).attr("data-catalog") === "1";
		if (isCatalog || !fieldname) {
			adv_case_nav_set_route("List", doctype);
			return;
		}
		adv_case_nav_set_route("List", doctype, { [fieldname]: caseName });
	});

	$w.find(".adv-hub-summary-pill__add").on("click", function (e) {
		e.preventDefault();
		e.stopPropagation();
		const doctype = $(this).attr("data-doctype");
		const fieldname = $(this).attr("data-fieldname");
		const defaults = {};
		if (fieldname) {
			defaults[fieldname] = caseName;
			if (frm.doc.client) {
				defaults.client = frm.doc.client;
			}
		}
		adv_case_nav_new_doc(doctype, defaults);
	});
}

function _adv_hub_bind_routes($w) {
	$w.find("[data-route]").on("click", function () {
		adv_case_nav_follow_route($(this).attr("data-route"));
	});
}

function _adv_hub_empty(icon, title, hint, btnLabel, actionName) {
	const cta =
		btnLabel && actionName
			? `<button type="button" class="adv-hub-empty__action" data-hub-action="${actionName}">${frappe.utils.escape_html(
					btnLabel
			  )}</button>`
			: "";
	return `<div class="adv-hub-empty">
		<div class="adv-hub-empty__icon">${icon}</div>
		<p class="adv-hub-empty__title">${frappe.utils.escape_html(title)}</p>
		${
			hint
				? `<p class="adv-hub-empty__hint">${frappe.utils.escape_html(hint)}</p>`
				: ""
		}
		${cta}
	</div>`;
}

function _adv_hub_status_badge(status) {
	const map = {
		Recebido: "green",
		Repassado: "green",
		Realizada: "green",
		"Concluída": "green",
		"Concluído": "green",
		Vencida: "red",
		Vencido: "red",
		Pendente: "orange",
		Agendada: "blue",
		"Em Andamento": "blue",
		Cancelada: "gray",
		Cancelado: "gray",
	};
	return `<span class="adv-hub-badge adv-hub-badge--${
		map[status] || "gray"
	}" style="margin-left:8px">${status || ""}</span>`;
}
