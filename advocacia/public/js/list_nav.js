frappe.provide("advocacia.list_nav");

(function () {
	function filters_to_route_options(filters) {
		var opts = {};
		(filters || []).forEach(function (filter) {
			if (!filter || filter.length < 3) {
				return;
			}
			var fieldname;
			var operator;
			var value;
			if (filter.length >= 4) {
				fieldname = filter[1];
				operator = filter[2];
				value = filter[3];
			} else {
				fieldname = filter[0];
				operator = filter[1];
				value = filter[2];
			}
			if (operator === "=" && !Array.isArray(value)) {
				opts[fieldname] = value;
			} else {
				opts[fieldname] = [operator, value];
			}
		});
		return opts;
	}

	advocacia.list_nav.goto = function (doctype, filters) {
		if (!doctype) {
			return;
		}
		frappe.set_route("List", doctype, filters_to_route_options(filters || []));
	};

	function open_connection_list(frm, $link, show_open) {
		if (!frm || frm.doc.__islocal || !$link || !$link.length) {
			return false;
		}

		var doctype = $link.attr("data-doctype");
		if (!doctype) {
			return false;
		}

		var names = ($link.attr("data-names") || "").split(",").filter(Boolean);
		if (names.length) {
			frappe.set_route("List", doctype, { name: ["in", names] });
			return true;
		}

		var dashboard = frm.dashboard;
		if (!dashboard || !dashboard.data || !dashboard.data.fieldname) {
			return false;
		}

		if (show_open && frappe.ui.notifications) {
			frappe.ui.notifications.show_open_count_list(doctype);
		}

		frappe.set_route("List", doctype, dashboard.get_document_filter(doctype));
		return true;
	}

	function on_count_click(e) {
		var count_el = e.target.closest(".form-dashboard .document-link .count");
		if (!count_el) {
			return;
		}

		var frm = frappe.ui.form.get_open_form();
		if (!frm || frm.doc.__islocal) {
			return;
		}

		var $link = $(count_el).closest(".document-link");
		if (!open_connection_list(frm, $link, false)) {
			return;
		}

		e.preventDefault();
		e.stopPropagation();
		e.stopImmediatePropagation();
	}

	function patch_dashboard_open_list() {
		if (!frappe.ui || !frappe.ui.form || !frappe.ui.form.Dashboard) {
			return false;
		}
		if (frappe.ui.form.Dashboard.prototype.__advocacia_connection_patched) {
			return true;
		}

		frappe.ui.form.Dashboard.prototype.open_document_list = function ($link, show_open) {
			open_connection_list(this.frm, $link, show_open);
		};

		frappe.ui.form.Dashboard.prototype.__advocacia_connection_patched = true;
		return true;
	}

	function patch_route_options_from_url() {
		if (!frappe.router || frappe.router.__advocacia_route_options_patched) {
			return !!frappe.router;
		}

		var _orig = frappe.router.set_route_options_from_url.bind(frappe.router);
		frappe.router.set_route_options_from_url = function () {
			_orig();
			Object.keys(frappe.route_options || {}).forEach(function (key) {
				var val = frappe.route_options[key];
				if (typeof val !== "string") {
					return;
				}
				try {
					frappe.route_options[key] = JSON.parse(val);
				} catch (e) {
					/* valor simples na query string */
				}
			});
		};

		frappe.router.__advocacia_route_options_patched = true;
		return true;
	}

	function ensure_patches(retries) {
		retries = retries || 0;
		var ok = patch_dashboard_open_list() && patch_route_options_from_url();
		if (!ok && retries < 40) {
			setTimeout(function () {
				ensure_patches(retries + 1);
			}, 250);
		}
	}

	function init() {
		document.addEventListener("click", on_count_click, true);
		ensure_patches(0);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
