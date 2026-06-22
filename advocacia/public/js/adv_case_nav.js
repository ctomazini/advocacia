/* Navegação hub ↔ satélites: breadcrumb do serviço, voltar e restaurar aba. */
(function () {
	const ADV_CASE_NAV_VERSION = 2;
	const BREADCRUMB_PATCH_VERSION = 2;
	const RENDER_FORM_PATCH_VERSION = 1;
	const BREADCRUMB_WIDTH_PATCH_VERSION = 1;
	const HUB_CONTEXT_KEY = "adv_hub_return_context";
	const CASE_DOCTYPE = "Legal Case";

	const CASE_FIELD_BY_DOCTYPE = {};

	const SATELLITE_DOCTYPES = [
		"Case Document",
		"Deadline",
		"Fee Agreement",
		"Hearing",
		"Court Cost",
		"Service Record",
		"Case Communication",
		"Time Entry",
		"Legal Task",
		"Legal Payment",
	];

	const HUB_NAV_DOCTYPES = [CASE_DOCTYPE, ...SATELLITE_DOCTYPES];

	// Labels via Translation seed (setup/translations.py) — use __(doctype) no client.
	function get_doctype_label(doctype) {
		return __(doctype);
	}

	function get_case_fieldname(doctype) {
		return CASE_FIELD_BY_DOCTYPE[doctype] || "legal_case";
	}

	function get_route_docname(route) {
		route = route || frappe.get_route();
		if (route[0] !== "Form" || !route[1]) {
			return null;
		}
		const docname = route.slice(2).join("/");
		return docname || null;
	}

	function get_case_name(frm, route) {
		route = route || frappe.get_route();
		if (!frm) {
			return null;
		}
		if (frm.doctype === CASE_DOCTYPE) {
			return frm.doc?.name || null;
		}

		const fieldname = get_case_fieldname(frm.doctype);
		if (frm.doc?.[fieldname]) {
			return frm.doc[fieldname];
		}

		const docname = get_route_docname(route);
		let doc = frm.doc;
		if (docname && (!doc || doc.name !== docname)) {
			doc = frappe.get_doc(frm.doctype, docname) || doc;
		}
		return doc?.[fieldname] || null;
	}

	function get_case_title(case_name) {
		if (!case_name) {
			return "";
		}
		const doc = frappe.get_doc?.(CASE_DOCTYPE, case_name);
		return doc?.title || case_name;
	}

	function case_form_route(case_name) {
		return `/desk/${frappe.router.slug(CASE_DOCTYPE)}/${encodeURIComponent(case_name)}`;
	}

	function build_case_crumb(frm, route) {
		if (frm.doctype === CASE_DOCTYPE) {
			return null;
		}

		const case_name = get_case_name(frm, route);
		if (!case_name) {
			return null;
		}

		return {
			route: case_form_route(case_name),
			label: case_name,
			css_classes: "adv-hub-case-crumb",
			parent_class: "ellipsis",
		};
	}

	function is_satellite_doctype(doctype) {
		return SATELLITE_DOCTYPES.includes(doctype);
	}

	function is_hub_nav_doctype(doctype) {
		return HUB_NAV_DOCTYPES.includes(doctype);
	}

	function get_frm_for_route(route) {
		route = route || frappe.get_route();
		if (route[0] !== "Form" || !route[1]) {
			return null;
		}

		const docname = get_route_docname(route);
		if (
			cur_frm &&
			cur_frm.doctype === route[1] &&
			(!docname || cur_frm.doc?.name === docname || cur_frm.is_new())
		) {
			return cur_frm;
		}

		const doctype_layout = frappe.router.doctype_layout || route[1];
		return (
			frappe.views.formview?.[doctype_layout]?.frm ||
			frappe.views.formview?.[route[1]]?.frm ||
			null
		);
	}

	function is_active_form_route(frm, route) {
		route = route || frappe.get_route();
		if (route[0] !== "Form" || route[1] !== frm.doctype) {
			return false;
		}
		return Boolean(get_route_docname(route));
	}

	function should_render_form_trail(frm, route) {
		if (!frm?.page?.$title_area || frm.meta?.istable) {
			return false;
		}
		route = route || frappe.get_route();
		return is_hub_nav_doctype(frm.doctype) && is_active_form_route(frm, route);
	}

	function get_form_breadcrumb_ul(frm) {
		if (frm?.page?.$title_area?.length) {
			const $in_title = frm.page.$title_area.find("ul.navbar-breadcrumbs").first();
			if ($in_title.length) {
				return $in_title;
			}
		}

		const $visible = $(frappe.container?.page).find("ul.navbar-breadcrumbs").first();
		if ($visible.length) {
			return $visible;
		}

		return $(".navbar-breadcrumbs").first();
	}

	function bind_breadcrumb_clicks($ul) {
		if (!$ul?.length) {
			return;
		}

		$ul.find("a[href^='/desk/']").off("click.adv_case_nav").on("click.adv_case_nav", function (event) {
			event.preventDefault();
			const href = $(this).attr("href") || "";
			const path = href.replace(/^\/desk\/?/, "");
			if (!path) {
				return;
			}
			frappe.set_route(path.split("/"));
		});
	}

	function build_workspace_crumb() {
		if (!frappe.app?.sidebar?.sidebar_title) {
			return null;
		}

		const icon = frappe.utils.get_desktop_icon_by_label(frappe.app.sidebar.sidebar_title);
		if (!icon) {
			return null;
		}

		const url = frappe.utils.get_route_for_icon(icon);
		if (!url) {
			return null;
		}

		return {
			route: url,
			label: __(icon.label),
			css_classes: "worksapce-breadcrumb",
			parent_class: "ellipsis",
		};
	}

	function build_list_crumb(doctype) {
		const doctype_meta = frappe.get_meta(doctype);
		if (
			(doctype === "User" && !frappe.user.has_role("System Manager")) ||
			doctype_meta?.issingle
		) {
			return null;
		}

		const doctype_route = frappe.router.slug(frappe.router.doctype_layout || doctype);
		let route;
		if (doctype_meta?.is_tree) {
			const view = frappe.model.user_settings[doctype]?.last_view || "Tree";
			route = `${doctype_route}/view/${view}`;
		} else {
			route = doctype_route;
		}

		return {
			route: `/desk/${route}`,
			label: __(doctype),
			css_classes: "title-text",
			parent_class: "ellipsis",
		};
	}

	function build_form_crumb(frm, route) {
		const doctype = frm.doctype;
		const docname = get_route_docname(route);
		const doc = frappe.get_doc(doctype, docname) || frm.doc;
		const form_route = `/desk/${frappe.router.slug(doctype)}/${encodeURIComponent(docname)}`;

		let docname_title;
		if (docname.startsWith("new-" + doctype.toLowerCase().replace(/ /g, "-"))) {
			docname_title = __("New {0}", [__(doctype)]);
		} else {
			docname_title = doc?.name || docname;
		}

		return {
			route: form_route,
			label: docname_title,
			css_classes: "title-text-form",
			disabled: true,
			ellipsis: frappe.is_mobile(),
		};
	}

	function build_breadcrumb_trail(frm, route) {
		route = route || frappe.get_route();
		const items = [];

		const workspace = build_workspace_crumb();
		if (workspace) {
			items.push(workspace);
		}

		const legal_case = build_case_crumb(frm, route);
		if (legal_case) {
			items.push(legal_case);
		}

		const list = build_list_crumb(frm.doctype);
		if (list) {
			items.push(list);
		}

		items.push(build_form_crumb(frm, route));
		return items;
	}

	function append_breadcrumb_li($ul, item) {
		const el = document.createElement("li");
		if (item.parent_class) {
			item.parent_class.split(/\s+/).forEach((cls) => {
				if (cls) {
					el.classList.add(cls);
				}
			});
		}
		if (item.disabled) {
			el.classList.add("disabled");
		}
		if (item.ellipsis) {
			el.classList.add("ellipsis");
		}

		const a = document.createElement("a");
		if (item.route) {
			a.href = item.route;
		}
		if (item.css_classes) {
			item.css_classes.split(/\s+/).forEach((cls) => {
				if (cls) {
					a.classList.add(cls);
				}
			});
		}
		if (item.ellipsis) {
			a.classList.add("ellipsis");
		}
		a.innerHTML = item.label;
		el.appendChild(a);
		$ul.append(el);
	}

	function render_breadcrumb_items($ul, items) {
		$ul.empty();

		const home_el = document.createElement("li");
		const home_a = document.createElement("a");
		home_a.href = "/desk";
		home_a.innerHTML = frappe.utils.icon("home");
		home_el.appendChild(home_a);
		$ul.append(home_el);

		items.forEach((item) => append_breadcrumb_li($ul, item));
		$("body").addClass("no-breadcrumbs");
	}

	function render_form_breadcrumb_trail(frm, route) {
		route = route || frappe.get_route();
		frm = frm || get_frm_for_route(route);
		if (!should_render_form_trail(frm, route)) {
			return;
		}

		const $ul = get_form_breadcrumb_ul(frm);
		if (!$ul.length) {
			return;
		}

		render_breadcrumb_items($ul, build_breadcrumb_trail(frm, route));
		bind_breadcrumb_clicks($ul);
	}

	function sync_form_breadcrumbs(frm) {
		render_form_breadcrumb_trail(frm);
	}

	const breadcrumb_sync_timers = new WeakMap();

	function queue_breadcrumb_sync(frm) {
		if (!frm) {
			return;
		}

		const existing = breadcrumb_sync_timers.get(frm);
		if (existing) {
			existing.forEach((timer_id) => clearTimeout(timer_id));
		}

		const timers = [0, 60, 200, 500].map((delay) =>
			setTimeout(() => sync_form_breadcrumbs(frm), delay)
		);
		breadcrumb_sync_timers.set(frm, timers);
	}

	function ensure_breadcrumb_registry(doctype) {
		const route_key = frappe.breadcrumbs.current_page();
		if (frappe.breadcrumbs.all[route_key]) {
			return frappe.breadcrumbs.all[route_key];
		}

		const meta = frappe.get_meta(doctype);
		if (!meta?.module) {
			return null;
		}

		const entry = {
			module: meta.module,
			doctype,
		};
		frappe.breadcrumbs.all[route_key] = entry;
		return entry;
	}

	function patch_breadcrumbs() {
		if (!frappe.breadcrumbs) {
			return;
		}
		if (frappe.breadcrumbs.__adv_case_nav_patched) {
			return;
		}

		const original_update = frappe.breadcrumbs.update.bind(frappe.breadcrumbs);
		const original_clear = frappe.breadcrumbs.clear.bind(frappe.breadcrumbs);

		frappe.breadcrumbs.clear = function () {
			const route = frappe.get_route();
			if (route[0] === "Form" && route[1] && is_hub_nav_doctype(route[1])) {
				const frm = get_frm_for_route(route) || cur_frm;
				this.$breadcrumbs = frm ? get_form_breadcrumb_ul(frm) : $();
				if (this.$breadcrumbs?.length) {
					this.$breadcrumbs.empty();
					return;
				}
			}

			return original_clear.call(this);
		};

		frappe.breadcrumbs.append_breadcrumb_element = function (route, label, css_classes) {
			if (!this.$breadcrumbs?.length) {
				const frm = get_frm_for_route() || cur_frm;
				this.$breadcrumbs = frm ? get_form_breadcrumb_ul(frm) : $();
			}
			if (!this.$breadcrumbs?.length) {
				const $visible = $(frappe.container?.page).find("ul.navbar-breadcrumbs").first();
				this.$breadcrumbs = $visible.length ? $visible : $(".navbar-breadcrumbs").first();
			}
			if (!this.$breadcrumbs?.length) {
				return;
			}

			const el = document.createElement("li");
			const a = document.createElement("a");
			if (route) {
				a.href = route;
			}
			if (css_classes) {
				a.classList.add(css_classes);
			}
			a.innerHTML = label;
			el.appendChild(a);
			this.$breadcrumbs.eq(0).append(el);
			bind_breadcrumb_clicks(this.$breadcrumbs);
		};

		frappe.breadcrumbs.update = function () {
			const route = frappe.get_route();
			if (route[0] === "Form" && route[1] && is_hub_nav_doctype(route[1])) {
				const frm = get_frm_for_route(route) || cur_frm;
				if (frm && frm.doctype === route[1]) {
					ensure_breadcrumb_registry(route[1]);
					const $ul = get_form_breadcrumb_ul(frm);
					if ($ul.length) {
						this.$breadcrumbs = $ul;
						render_form_breadcrumb_trail(frm, route);
						this.toggle(true);
						return;
					}
					queue_breadcrumb_sync(frm);
				}
			}

			return original_update.call(this);
		};

		frappe.breadcrumbs.__adv_case_nav_version = BREADCRUMB_PATCH_VERSION;
		frappe.breadcrumbs.__adv_case_nav_patched = true;
	}

	function patch_configure_breadcrumb_width() {
		const proto = frappe.ui?.form?.Form?.prototype;
		if (!proto || proto.__adv_case_nav_breadcrumb_version >= BREADCRUMB_WIDTH_PATCH_VERSION) {
			return;
		}

		if (!proto.__adv_case_nav_original_configure_breadcrumb_width) {
			proto.__adv_case_nav_original_configure_breadcrumb_width =
				proto.configure_breadcrumb_width;
		}
		const original = proto.__adv_case_nav_original_configure_breadcrumb_width;
		proto.configure_breadcrumb_width = function () {
			original.call(this);
			if (should_render_form_trail(this)) {
				setTimeout(() => render_form_breadcrumb_trail(this), 200);
			}
		};
		proto.__adv_case_nav_breadcrumb_version = BREADCRUMB_WIDTH_PATCH_VERSION;
		proto.__adv_case_nav_breadcrumb_patched = true;
	}

	function patch_form_render_form() {
		const proto = frappe.ui?.form?.Form?.prototype;
		if (!proto || proto.__adv_case_nav_render_version >= RENDER_FORM_PATCH_VERSION) {
			return;
		}

		if (!proto.__adv_case_nav_original_render_form) {
			proto.__adv_case_nav_original_render_form = proto.render_form;
		}
		const original_render_form = proto.__adv_case_nav_original_render_form;
		proto.render_form = function (...args) {
			const result = original_render_form.apply(this, args);
			if (is_hub_nav_doctype(this.doctype)) {
				this.$wrapper.one("render_complete", () => {
					queue_breadcrumb_sync(this);
				});
			}
			return result;
		};
		proto.__adv_case_nav_render_version = RENDER_FORM_PATCH_VERSION;
		proto.__adv_case_nav_render_patched = true;
	}

	function detect_active_hub_tab(frm) {
		if (!frm?.$wrapper) {
			return "tab_details";
		}
		const $active = frm.$wrapper.find(".form-tabs-list .nav-link.active");
		const fieldname = $active.attr("data-fieldname");
		if (fieldname && fieldname.startsWith("tab_")) {
			return fieldname;
		}
		return "tab_details";
	}

	function save_hub_context(frm, tab_fieldname) {
		if (!frm || frm.doctype !== CASE_DOCTYPE || frm.is_new() || !frm.doc.name) {
			return;
		}
		sessionStorage.setItem(
			HUB_CONTEXT_KEY,
			JSON.stringify({
				legal_case: frm.doc.name,
				tab: tab_fieldname || detect_active_hub_tab(frm),
			})
		);
	}

	function save_hub_context_from_cur_frm(tab_fieldname) {
		if (cur_frm && cur_frm.doctype === CASE_DOCTYPE) {
			save_hub_context(cur_frm, tab_fieldname);
		}
	}

	function restore_hub_tab(frm) {
		const raw = sessionStorage.getItem(HUB_CONTEXT_KEY);
		if (!raw || !frm || frm.doctype !== CASE_DOCTYPE || frm.is_new()) {
			return;
		}

		let context;
		try {
			context = JSON.parse(raw);
		} catch (error) {
			sessionStorage.removeItem(HUB_CONTEXT_KEY);
			return;
		}

		if (!context?.legal_case || context.legal_case !== frm.doc.name || !context.tab) {
			return;
		}

		sessionStorage.removeItem(HUB_CONTEXT_KEY);

		setTimeout(() => {
			const tab_field = frm.fields_dict[context.tab];
			if (tab_field?.tab_link) {
				$(tab_field.tab_link).trigger("click");
				return;
			}
			const $tab = frm.$wrapper.find(
				`.form-tabs-list .nav-link[data-fieldname="${context.tab}"]`
			);
			if ($tab.length) {
				$tab.trigger("click");
			}
		}, 300);
	}

	function add_back_to_case_button(frm) {
		const case_name = get_case_name(frm);
		if (!case_name || frm.is_new() || frm.doctype === CASE_DOCTYPE) {
			return;
		}

		frm.add_custom_button(__("Voltar ao Processo"), () => {
			frappe.set_route("Form", CASE_DOCTYPE, case_name);
		});
		frm.change_custom_button_type(__("Voltar ao Processo"), null, "primary");
	}

	function bind_satellite_forms() {
		SATELLITE_DOCTYPES.forEach((doctype) => {
			frappe.ui.form.on(doctype, {
				refresh(frm) {
					add_back_to_case_button(frm);
					queue_breadcrumb_sync(frm);
				},
			});
		});

		frappe.ui.form.on(CASE_DOCTYPE, {
			refresh(frm) {
				restore_hub_tab(frm);
				queue_breadcrumb_sync(frm);
			},
		});
	}

	function bind_breadcrumb_sync() {
		$(document).on("form-refresh", (event, frm) => {
			queue_breadcrumb_sync(frm);
		});

		$(document).on("form-load", (event, frm) => {
			queue_breadcrumb_sync(frm);
		});

		$(document).on("page-change", () => {
			const route = frappe.get_route();
			const frm = get_frm_for_route(route) || cur_frm;
			if (frm) {
				queue_breadcrumb_sync(frm);
			}
		});
	}

	function publish_adv_case_nav_api() {
		window.adv_case_nav = {
			VERSION: ADV_CASE_NAV_VERSION,
			HUB_CONTEXT_KEY,
			SATELLITE_DOCTYPES,
			CASE_FIELD_BY_DOCTYPE,
			get_doctype_label,
			get_case_fieldname,
			get_case_name,
			get_case_title,
			get_frm_for_route,
			get_form_breadcrumb_ul,
			save_hub_context,
			restore_hub_tab,
			sync_form_breadcrumbs,
			render_form_breadcrumb_trail,
			is_satellite_doctype,
			debug_breadcrumbs() {
				const route = frappe.get_route();
				const frm = get_frm_for_route(route) || cur_frm;
				const $ul = frm ? get_form_breadcrumb_ul(frm) : $();
				const info = {
					version: ADV_CASE_NAV_VERSION,
					route: route.join("/"),
					frm: frm?.doctype,
					ul_count: $ul.length,
					li_count: $ul.find("li").length,
					case_name: frm ? get_case_name(frm, route) : null,
				};
				console.log("[adv_case_nav]", info);
				if (frm) {
					sync_form_breadcrumbs(frm);
					info.li_after_render = get_form_breadcrumb_ul(frm).find("li").length;
					console.log("[adv_case_nav] after render", info.li_after_render);
				}
				return info;
			},
		};
	}

	function init_adv_case_nav() {
		publish_adv_case_nav_api();

		if (!window.frappe?.breadcrumbs || !window.frappe?.ui?.form?.Form) {
			setTimeout(init_adv_case_nav, 50);
			return;
		}

		patch_breadcrumbs();
		patch_configure_breadcrumb_width();
		patch_form_render_form();

		if (window.__adv_case_nav_initialized) {
			return;
		}

		window.__adv_case_nav_initialized = true;
		bind_satellite_forms();
		bind_breadcrumb_sync();
	}

	window.adv_case_nav_follow_route = function (route_str) {
		save_hub_context_from_cur_frm();
		const parts = (route_str || "").split("/");
		frappe.set_route(parts[0], parts[1], parts[2]);
	};

	window.adv_case_nav_new_doc = function (doctype, defaults) {
		save_hub_context_from_cur_frm();
		frappe.route_options = defaults || {};
		frappe.set_route("Form", doctype, "new");
	};

	window.adv_case_nav_set_route = function () {
		save_hub_context_from_cur_frm();
		frappe.set_route.apply(frappe, arguments);
	};

	window.adv_case_nav_restore_tab = restore_hub_tab;

	init_adv_case_nav();
})();
