frappe.provide("advocacia.list_nav");

(function () {
	var pending = {
		doctype: null,
		mode: null,
		filters: null,
	};

	var sidebar_clear_doctype = null;

	function get_list_view(doctype) {
		var key = "List/" + doctype + "/List";
		return frappe.views.list_view && frappe.views.list_view[key];
	}

	function reset_saved_filters(listview) {
		listview.filters = [];
		if (listview.view_user_settings) {
			listview.view_user_settings.filters = [];
		}
	}

	function apply_filter_state(listview, filters) {
		if (!listview || !listview.filter_area) {
			return Promise.resolve(false);
		}

		listview.filters = (filters || []).slice();
		reset_saved_filters(listview);

		return listview.filter_area
			.clear(false)
			.then(function () {
				if (listview.filters.length) {
					return listview.filter_area.set(listview.filters);
				}
			})
			.then(function () {
				listview.refresh();
				return true;
			});
	}

	function consume_pending(listview) {
		if (!pending.doctype || pending.doctype !== listview.doctype) {
			return null;
		}

		var mode = pending.mode;
		var filters = pending.filters || [];
		pending.doctype = null;
		pending.mode = null;
		pending.filters = null;

		return mode === "clear" ? [] : filters.slice();
	}

	advocacia.list_nav.goto = function (doctype, filters) {
		filters = filters || [];
		pending.doctype = doctype;
		pending.mode = filters.length ? "set" : "clear";
		pending.filters = filters.map(function (f) {
			return [doctype, f[0], f[1], f[2]];
		});
		frappe.route_options = null;

		var route = frappe.get_route() || [];
		if (route[0] === "List" && route[1] === doctype) {
			var listview = get_list_view(doctype);
			if (listview) {
				apply_filter_state(
					listview,
					pending.mode === "clear" ? [] : pending.filters.slice()
				);
				pending.doctype = null;
				pending.mode = null;
				pending.filters = null;
				return;
			}
		}

		frappe.set_route("List", doctype);
	};

	function bind_page_change() {
		$(document).on("page-change", function () {
			var route = frappe.get_route() || [];
			if (route[0] !== "List" || !route[1]) {
				return;
			}
			if (pending.doctype === route[1]) {
				return;
			}
			sidebar_clear_doctype = route[1];
		});
	}

	function patch_list_view() {
		if (!frappe.views || !frappe.views.ListView) {
			return false;
		}
		if (frappe.views.ListView.prototype.__advocacia_list_nav_patched) {
			return true;
		}

		var _before_refresh = frappe.views.ListView.prototype.before_refresh;

		frappe.views.ListView.prototype.before_refresh = function () {
			var listview = this;
			var nav_filters = consume_pending(listview);

			if (nav_filters !== null) {
				frappe.route_options = null;
				listview.filters = nav_filters.slice();
				reset_saved_filters(listview);

				if (listview.filter_area) {
					return listview.filter_area.clear(false).then(function () {
						if (listview.filters.length) {
							return listview.filter_area.set(listview.filters);
						}
					});
				}
				return Promise.resolve();
			}

			if (sidebar_clear_doctype === listview.doctype) {
				sidebar_clear_doctype = null;
				reset_saved_filters(listview);

				if (listview.filter_area) {
					return listview.filter_area.clear(false);
				}
				return Promise.resolve();
			}

			return _before_refresh.call(listview);
		};

		frappe.views.ListView.prototype.__advocacia_list_nav_patched = true;
		return true;
	}

	function init() {
		bind_page_change();
		if (!patch_list_view()) {
			$(document).one("app_ready", init);
		}
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
