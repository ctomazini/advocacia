/* ═══════════════════════════════════════════════════════════
   adv_hub — Render functions for Legal Case hub tabs
   ═══════════════════════════════════════════════════════════ */

window.advocacia = window.advocacia || {};

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
			_adv_hub_empty("⚖️", __("Nenhuma audiência cadastrada"), __("+ Audiência"), "new-hearing")
		);
		$w.find('[data-hub-action="new-hearing"]').on("click", () => {
			frappe.new_doc("Hearing", {
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
				${__("Audiências")}
				<span class="adv-hub-panel__count">${hearings.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-hearing">
				${__("+ Audiência")}
			</button>
		</div>
		${items}
	</div>`);

	$w.find('[data-hub-action="new-hearing"]').on("click", () => {
		frappe.new_doc("Hearing", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_deadlines(frm, deadlines) {
	const $w = frm.fields_dict.deadlines_panel?.$wrapper;
	if (!$w) return;

	if (!deadlines.length) {
		$w.html(
			_adv_hub_empty("📅", __("Nenhum prazo cadastrado"), __("+ Prazo"), "new-deadline")
		);
		$w.find('[data-hub-action="new-deadline"]').on("click", () => {
			frappe.new_doc("Deadline", { legal_case: frm.doc.name, client: frm.doc.client });
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
				${__("Prazos")}
				<span class="adv-hub-panel__count">${deadlines.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-deadline">
				${__("+ Prazo")}
			</button>
		</div>
		${items}
	</div>`);

	$w.find('[data-hub-action="new-deadline"]').on("click", () => {
		frappe.new_doc("Deadline", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_tasks(frm, tasks) {
	const $w = frm.fields_dict.tasks_panel?.$wrapper;
	if (!$w) return;

	if (!tasks.length) {
		$w.html(
			_adv_hub_empty("✅", __("Nenhuma tarefa pendente"), __("+ Tarefa"), "new-task")
		);
		$w.find('[data-hub-action="new-task"]').on("click", () => {
			frappe.new_doc("Legal Task", { legal_case: frm.doc.name, client: frm.doc.client });
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
				${__("Tarefas")}
				<span class="adv-hub-panel__count">${tasks.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-task">
				${__("+ Tarefa")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-task"]').on("click", () => {
		frappe.new_doc("Legal Task", { legal_case: frm.doc.name, client: frm.doc.client });
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
				__("Nenhuma comunicação registrada"),
				__("+ Comunicação"),
				"new-comm"
			)
		);
		$w.find('[data-hub-action="new-comm"]').on("click", () => {
			frappe.new_doc("Case Communication", {
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
				${__("Comunicações")}
				<span class="adv-hub-panel__count">${communications.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-comm">
				${__("+ Comunicação")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-comm"]').on("click", () => {
		frappe.new_doc("Case Communication", {
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
			_adv_hub_empty("📝", __("Nenhum registro de atos"), __("+ Registro"), "new-record")
		);
		$w.find('[data-hub-action="new-record"]').on("click", () => {
			frappe.new_doc("Service Record", { legal_case: frm.doc.name, client: frm.doc.client });
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
					"{0} ato(s)",
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
				${__("Registro de Atos")}
				<span class="adv-hub-panel__count">${records.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-record">
				${__("+ Registro")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-record"]').on("click", () => {
		frappe.new_doc("Service Record", { legal_case: frm.doc.name, client: frm.doc.client });
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
			_adv_hub_empty("⏱️", __("Nenhum registro de horas"), __("+ Horas"), "new-time")
		);
		$w.find('[data-hub-action="new-time"]').on("click", () => {
			frappe.new_doc("Time Entry", { legal_case: frm.doc.name, client: frm.doc.client });
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
				${__("Registro de Horas")}
				<span class="adv-hub-panel__count">${items.length}</span>
			</h3>
			<div class="adv-hub-panel__actions">
				<span class="text-muted small">${__("Total")}: <strong>${totalHours}h</strong></span>
				<button type="button" class="adv-hub-panel__action" data-hub-action="new-time">
					${__("+ Horas")}
				</button>
			</div>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-time"]').on("click", () => {
		frappe.new_doc("Time Entry", { legal_case: frm.doc.name, client: frm.doc.client });
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
					${__("Documentos do Processo")}
					<span class="adv-hub-panel__count">0</span>
				</h3>
				${headerActions}
			</div>
			<div class="adv-hub-empty">
				<div class="adv-hub-empty__icon">📄</div>
				<div>${__("Nenhum documento registrado")}</div>
				<button type="button" class="adv-hub-empty__action" data-hub-action="new-document">
					${__("+ Enviar documento")}
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
				${__("Documentos do Processo")}
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
		frappe.new_doc("Case Document", {
			legal_case: frm.doc.name,
			client: frm.doc.client,
		});
	});
	$w.find('[data-hub-action="generate-docs"]').on("click", () => {
		if (typeof abrir_dialog_gerar_documentos === "function") {
			abrir_dialog_gerar_documentos(frm);
			return;
		}
		frappe.msgprint(__("Use o botão Gerar Documentos na barra de ações."));
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
				${__("Kits de Documentos")}
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
		if (typeof abrir_dialog_gerar_documentos === "function") {
			abrir_dialog_gerar_documentos(frm);
			return;
		}
		frappe.msgprint(__("Use o botão Gerar Documentos na barra de ações."));
	});
	$w.find(".adv-hub-kit-card").on("click", () => {
		if (typeof abrir_dialog_gerar_documentos === "function") {
			abrir_dialog_gerar_documentos(frm);
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
		panels.forEach((panel) => {
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

function _adv_hub_render_financial_summary(frm, financial) {
	const $w = frm.fields_dict.financial_summary_panel?.$wrapper;
	if (!$w) return;

	const summary = financial.summary || {};
	const agreement = financial.agreement;
	const total = summary.total_contract || 1;
	const pctReceived = total
		? Math.min(100, Math.round((summary.total_received / total) * 100))
		: 0;

	$w.html(`<div class="adv-hub-panel">
		<div class="adv-hub-panel__header">
			<h3 class="adv-hub-panel__title">
				<span class="adv-hub-panel__title-icon">💰</span>
				${__("Resumo Financeiro")}
			</h3>
			${
				agreement
					? `<button type="button" class="adv-hub-panel__action" data-route="Form/Fee Agreement/${frappe.utils.escape_html(
							agreement.name
					  )}">${__("Ver Acordo")}</button>`
					: `<button type="button" class="adv-hub-panel__action" data-hub-action="new-agreement">${__(
							"+ Acordo"
					  )}</button>`
			}
		</div>
		<div class="adv-hub-kpi-row">
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--blue-500)">${format_currency(
					summary.total_contract
				)}</div>
				<div class="adv-hub-kpi__label">${__("Contratado")}</div>
			</div>
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--green-600)">${format_currency(
					summary.total_received
				)}</div>
				<div class="adv-hub-kpi__label">${__("Recebido")}</div>
			</div>
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--orange-500)">${format_currency(
					summary.total_pending
				)}</div>
				<div class="adv-hub-kpi__label">${__("Pendente")}</div>
			</div>
			<div class="adv-hub-kpi">
				<div class="adv-hub-kpi__value" style="color:var(--red-500)">${format_currency(
					summary.total_costs
				)}</div>
				<div class="adv-hub-kpi__label">${__("Custas")}</div>
			</div>
		</div>
		<div class="adv-hub-stacked-bar" title="${__("{0}% recebido", [pctReceived])}">
			<div class="adv-hub-stacked-bar__segment" style="width:${pctReceived}%;background:var(--green-500)"></div>
		</div>
	</div>`);

	$w.find("[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
	$w.find('[data-hub-action="new-agreement"]').on("click", () => {
		frappe.new_doc("Fee Agreement", {
			legal_case: frm.doc.name,
			client: frm.doc.client,
		});
	});
}

function _adv_hub_render_installments(frm, installments) {
	const $w = frm.fields_dict.installments_panel?.$wrapper;
	if (!$w) return;

	if (!installments.length) {
		$w.html(`<div class="adv-hub-empty">${__("Nenhuma parcela registrada.")}</div>`);
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
				${__("Parcelas")}
				<span class="adv-hub-panel__count">${installments.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="list-agreements">
				${__("Ver Acordos")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="list-agreements"]').on("click", () => {
		frappe.set_route("List", "Fee Agreement", { legal_case: frm.doc.name });
	});
	_adv_hub_bind_routes($w);
}

function _adv_hub_render_payments(frm, payments) {
	const $w = frm.fields_dict.payments_panel?.$wrapper;
	if (!$w) return;

	if (!payments.length) {
		$w.html(
			_adv_hub_empty("💵", __("Nenhum pagamento registrado"), __("+ Pagamento"), "new-payment")
		);
		$w.find('[data-hub-action="new-payment"]').on("click", () => {
			frappe.new_doc("Legal Payment", {
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
				${__("Pagamentos")}
				<span class="adv-hub-panel__count">${payments.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-payment">
				${__("+ Pagamento")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-payment"]').on("click", () => {
		frappe.new_doc("Legal Payment", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function _adv_hub_render_court_costs(frm, costs) {
	const $w = frm.fields_dict.court_costs_panel?.$wrapper;
	if (!$w) return;

	if (!costs.length) {
		$w.html(
			_adv_hub_empty("🏛️", __("Nenhuma custa registrada"), __("+ Custa"), "new-cost")
		);
		$w.find('[data-hub-action="new-cost"]').on("click", () => {
			frappe.new_doc("Court Cost", { legal_case: frm.doc.name, client: frm.doc.client });
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
				${__("Custas Processuais")}
				<span class="adv-hub-panel__count">${costs.length}</span>
			</h3>
			<button type="button" class="adv-hub-panel__action" data-hub-action="new-cost">
				${__("+ Custa")}
			</button>
		</div>
		${rows}
	</div>`);

	$w.find('[data-hub-action="new-cost"]').on("click", () => {
		frappe.new_doc("Court Cost", { legal_case: frm.doc.name, client: frm.doc.client });
	});
	_adv_hub_bind_routes($w);
}

function adv_hub_render_summary_bar(frm, counts) {
	const $w = frm.fields_dict.hub_summary_bar?.$wrapper;
	if (!$w) return;

	const caseName = frm.doc.name;
	const items = [
		{
			icon: "📋",
			label: __("Fase"),
			count: counts.phases,
			doctype: "Legal Case",
			fieldname: "name",
			readonly: true,
		},
		{
			icon: "⚖️",
			label: __("Audiências"),
			count: counts.hearings,
			doctype: "Hearing",
			fieldname: "legal_case",
		},
		{
			icon: "📅",
			label: __("Prazos"),
			count: counts.deadlines,
			doctype: "Deadline",
			fieldname: "legal_case",
		},
		{
			icon: "✅",
			label: __("Tarefas"),
			count: counts.tasks,
			doctype: "Legal Task",
			fieldname: "legal_case",
		},
		{
			icon: "💬",
			label: __("Comunicações"),
			count: counts.communications,
			doctype: "Case Communication",
			fieldname: "legal_case",
		},
		{
			icon: "📝",
			label: __("Atos"),
			count: counts.service_records,
			doctype: "Service Record",
			fieldname: "legal_case",
		},
		{
			icon: "⏱️",
			label: __("Horas"),
			count: counts.time_entries,
			doctype: "Time Entry",
			fieldname: "legal_case",
		},
		{
			icon: "📄",
			label: __("Documentos"),
			count: counts.documents,
			doctype: "Case Document",
			fieldname: "legal_case",
		},
		{
			icon: "📦",
			label: __("Kits"),
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
				label: __("Acordos"),
				count: counts.fee_agreements,
				doctype: "Fee Agreement",
				fieldname: "legal_case",
			},
			{
				icon: "💳",
				label: __("Parcelas"),
				count: counts.installments,
				doctype: "Fee Agreement",
				fieldname: "legal_case",
				listOnly: true,
			},
			{
				icon: "💵",
				label: __("Pagamentos"),
				count: counts.payments,
				doctype: "Legal Payment",
				fieldname: "legal_case",
			},
			{
				icon: "🏛️",
				label: __("Custas"),
				count: counts.court_costs,
				doctype: "Court Cost",
				fieldname: "legal_case",
			}
		);
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
					: `<span class="adv-hub-summary-pill__add"
				data-doctype="${frappe.utils.escape_html(item.doctype)}"
				data-fieldname="${frappe.utils.escape_html(item.fieldname || "")}"
				data-list-only="${item.listOnly ? "1" : "0"}"
				data-catalog="${item.catalog ? "1" : "0"}"
				title="${frappe.utils.escape_html(__("Criar {0}", [item.label]))}">+</span>`
			}
		</div>`;
		})
		.join("");

	$w.html(`<div class="adv-hub-summary-bar">${pills}</div>`);

	$w.find(".adv-hub-summary-pill__link").on("click", function (e) {
		e.preventDefault();
		const doctype = $(this).attr("data-doctype");
		const fieldname = $(this).attr("data-fieldname");
		const isCatalog = $(this).attr("data-catalog") === "1";
		if (isCatalog || !fieldname) {
			frappe.set_route("List", doctype);
			return;
		}
		frappe.set_route("List", doctype, { [fieldname]: caseName });
	});

	$w.find(".adv-hub-summary-pill__add").on("click", function (e) {
		e.stopPropagation();
		const doctype = $(this).attr("data-doctype");
		const fieldname = $(this).attr("data-fieldname");
		const isCatalog = $(this).attr("data-catalog") === "1";
		const listOnly = $(this).attr("data-list-only") === "1";

		if (isCatalog) {
			frappe.set_route("List", doctype);
			return;
		}
		if (listOnly || !fieldname) {
			frappe.set_route("List", doctype, { [fieldname]: caseName });
			return;
		}
		frappe.new_doc(doctype, {
			[fieldname]: caseName,
			client: frm.doc.client,
		});
	});
}

function _adv_hub_bind_routes($w) {
	$w.find("[data-route]").on("click", function () {
		const parts = $(this).attr("data-route").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	});
}

function _adv_hub_empty(icon, msg, btnLabel, actionName) {
	return `<div class="adv-hub-empty">
		<div class="adv-hub-empty__icon">${icon}</div>
		<div>${msg}</div>
		<button type="button" class="adv-hub-empty__action" data-hub-action="${actionName}">${btnLabel}</button>
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
