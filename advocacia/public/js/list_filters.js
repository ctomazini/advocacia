frappe.provide("advocacia.list_filters");

(function () {
	var MOBILE_MAX_WIDTH = 768;
	var enhanced_areas = [];

	function is_mobile_layout() {
		return window.innerWidth < MOBILE_MAX_WIDTH;
	}

	function get_wrapper(filter_area) {
		if (filter_area.standard_filters_wrapper && filter_area.standard_filters_wrapper.length) {
			return filter_area.standard_filters_wrapper;
		}
		if (!filter_area.list_view || !filter_area.list_view.page) {
			return null;
		}
		var $wrapper = filter_area.list_view.page.page_form.find(".standard-filter-section");
		if ($wrapper.length) {
			filter_area.standard_filters_wrapper = $wrapper;
		}
		return $wrapper.length ? $wrapper : null;
	}

	function apply_responsive_filter_layout(filter_area) {
		var $wrapper = get_wrapper(filter_area);
		if (!$wrapper) {
			return false;
		}

		if (is_mobile_layout()) {
			$wrapper.removeClass("advocacia-filters-desktop-visible");
			if (filter_area.standard_filters_visible) {
				$wrapper.addClass("advocacia-filters-mobile-open").show();
			} else {
				$wrapper.removeClass("advocacia-filters-mobile-open").hide();
			}
		} else {
			filter_area.standard_filters_visible = true;
			$wrapper
				.removeClass("advocacia-filters-mobile-open")
				.addClass("advocacia-filters-desktop-visible")
				.show();
		}

		return true;
	}

	function wait_for_wrapper(filter_area, retries) {
		retries = retries || 0;
		if (apply_responsive_filter_layout(filter_area) || retries >= 40) {
			return;
		}
		setTimeout(function () {
			wait_for_wrapper(filter_area, retries + 1);
		}, 100);
	}

	advocacia.list_filters.enhance = function (filter_area) {
		if (!filter_area || filter_area.__advocacia_responsive_enhanced) {
			return;
		}

		filter_area.__advocacia_responsive_enhanced = true;
		enhanced_areas.push(filter_area);

		var _toggle = filter_area.toggle_standard_filter.bind(filter_area);
		filter_area.toggle_standard_filter = function () {
			_toggle();
			apply_responsive_filter_layout(filter_area);
		};

		wait_for_wrapper(filter_area, 0);
	};

	function refresh_all_filter_areas() {
		enhanced_areas.forEach(function (filter_area) {
			if (is_mobile_layout()) {
				filter_area.standard_filters_visible = false;
			}
			apply_responsive_filter_layout(filter_area);
		});
	}

	function patch_base_list() {
		if (!frappe.views || !frappe.views.BaseList) {
			return false;
		}
		if (frappe.views.BaseList.prototype.__advocacia_filter_responsive_patched) {
			return true;
		}

		var _setup_filter_area = frappe.views.BaseList.prototype.setup_filter_area;
		frappe.views.BaseList.prototype.setup_filter_area = function () {
			_setup_filter_area.call(this);
			if (this.filter_area) {
				advocacia.list_filters.enhance(this.filter_area);
			}
		};

		frappe.views.BaseList.prototype.__advocacia_filter_responsive_patched = true;
		return true;
	}

	function ensure_patches(retries) {
		retries = retries || 0;
		var ok = patch_base_list();
		if (!ok && retries < 40) {
			setTimeout(function () {
				ensure_patches(retries + 1);
			}, 250);
		}
	}

	function init() {
		window.addEventListener(
			"resize",
			frappe.utils.debounce(refresh_all_filter_areas, 200)
		);
		ensure_patches(0);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
