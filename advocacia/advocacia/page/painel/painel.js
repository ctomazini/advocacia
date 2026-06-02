frappe.pages.painel = frappe.pages.painel || {};

frappe.pages.painel.on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Painel do Escritório"),
        single_column: true,
    });

    page.painel_container = $('<div class="painel-root"></div>').appendTo(page.main);
    inject_painel_styles();
    painel_polish_frappe_chrome();

    page.add_button(__("↺ Atualizar"), function () {
        load_painel(page);
    });

    frappe.pages.painel.page = page;
    page.painel_periodo = 7;
    page.painel_list_limits = painel_default_list_limits();
    load_painel(page);
};

frappe.pages.painel.on_page_hide = function () {
    $(document.body).removeClass("advocacia-painel-active");
};

function painel_polish_frappe_chrome() {
    $(document.body).addClass("advocacia-painel-active");
}

function inject_painel_styles() {
    $("#painel-advocacia-styles").remove();
    var css = `
        .painel-root {
            --painel-radius: 16px;
            --painel-radius-sm: 12px;
            --painel-gap: 32px;
            --painel-gap-md: 24px;
            --painel-gap-sm: 16px;
            --painel-tone-red: var(--red-600);
            --painel-tone-orange: var(--orange-600);
            --painel-tone-yellow: var(--yellow-600);
            --painel-tone-green: var(--green-700);
            --painel-tone-blue: var(--blue-600);
            --painel-tone-gray: var(--gray-600);
            --painel-shadow: 0 1px 2px color-mix(in srgb, var(--gray-900) 4%, transparent),
                0 8px 24px color-mix(in srgb, var(--gray-900) 5%, transparent);
            --painel-shadow-hover: 0 2px 4px color-mix(in srgb, var(--gray-900) 5%, transparent),
                0 12px 32px color-mix(in srgb, var(--gray-900) 8%, transparent);
            max-width: 1280px;
            margin: 0 auto;
            padding: 12px 16px 64px;
            color: var(--text-color);
            -webkit-font-smoothing: antialiased;
            overflow: visible;
        }
        @media (min-width: 1024px) {
            .painel-root { padding: 12px 28px 64px; }
        }
        .painel-content {
            animation: painel-fade-in 0.45s ease-out;
        }
        @keyframes painel-fade-in {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .painel-hero {
            padding: 36px 0 28px;
            margin-bottom: var(--painel-gap-md);
            border-bottom: none;
        }
        .painel-hero-greeting {
            font-size: clamp(1.5rem, 3vw, 2rem);
            font-weight: 600;
            letter-spacing: -0.035em;
            line-height: 1.15;
            margin: 0 0 10px;
            color: var(--text-color);
        }
        .painel-hero-date {
            font-size: var(--text-base);
            color: var(--text-muted);
            margin: 0 0 8px;
            font-weight: 400;
        }
        .painel-hero-context {
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            gap: 6px 0;
            font-size: var(--text-sm);
            color: var(--text-muted);
            line-height: 1.55;
            max-width: 52rem;
            margin: 0 0 20px;
        }
        .painel-hero-context-part {
            display: inline;
        }
        .painel-hero-context-part + .painel-hero-context-part::before {
            content: " · ";
            white-space: pre;
            opacity: 0.55;
        }
        .painel-hero-money {
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
            color: var(--text-color);
            font-weight: 600;
        }
        .painel-hero-pulse {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px 24px;
            font-size: var(--text-sm);
            color: var(--text-muted);
            line-height: 1.5;
        }
        .painel-hero-pulse-stats {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px 20px;
        }
        .painel-hero-stat {
            display: inline-flex;
            flex-wrap: wrap;
            align-items: baseline;
            gap: 0.25em;
            max-width: 100%;
        }
        .painel-hero-stat--money {
            white-space: nowrap;
        }
        .painel-hero-pulse strong {
            color: var(--text-color);
            font-weight: 600;
        }
        .painel-hero-pulse .dot {
            width: 3px;
            height: 3px;
            border-radius: 50%;
            background: var(--text-muted);
            opacity: 0.35;
        }
        .painel-urgency-badge {
            display: inline-flex;
            align-items: center;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.01em;
        }
        .painel-urgency-badge.alta {
            background: color-mix(in srgb, var(--red-500) 10%, var(--card-bg));
            color: var(--red-600);
            border: 1px solid color-mix(in srgb, var(--red-500) 22%, transparent);
        }
        .painel-urgency-badge.normal {
            background: color-mix(in srgb, var(--green-500) 8%, var(--card-bg));
            color: var(--green-700);
            border: 1px solid color-mix(in srgb, var(--green-500) 18%, transparent);
        }
        .painel-actions-wrap {
            margin-bottom: var(--painel-gap-md);
        }
        .painel-actions-label {
            display: none;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin: 0 0 10px;
        }
        .painel-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .painel-action-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 11px 18px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 80%, transparent);
            background: var(--card-bg);
            color: var(--text-color);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.18s ease, background 0.22s ease;
            min-height: 44px;
            box-shadow: var(--painel-shadow);
        }
        .painel-action-chip .icon {
            color: var(--primary);
            flex-shrink: 0;
        }
        .painel-action-chip:hover {
            border-color: color-mix(in srgb, var(--primary) 35%, var(--border-color));
            box-shadow: var(--painel-shadow-hover);
            transform: translateY(-1px);
            background: color-mix(in srgb, var(--primary) 4%, var(--card-bg));
        }
        .painel-section { margin-bottom: var(--painel-gap); }
        .painel-section--primary { margin-bottom: calc(var(--painel-gap) + 8px); }
        .painel-section-head {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-bottom: 20px;
            gap: 16px;
        }
        .painel-section-title {
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: var(--text-color);
            margin: 0;
            line-height: 1.3;
        }
        .painel-section-sub {
            font-size: 13px;
            color: var(--text-muted);
            margin: 6px 0 0;
            font-weight: 400;
            line-height: 1.45;
        }
        .painel-section-link {
            font-size: 13px;
            color: var(--primary);
            cursor: pointer;
            font-weight: 500;
            opacity: 0.9;
            transition: opacity 0.15s ease;
            white-space: nowrap;
        }
        .painel-section-link:hover { opacity: 1; }
        .painel-kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        .painel-kpi {
            position: relative;
            padding: 28px 24px 24px;
            border-radius: var(--painel-radius);
            background: var(--card-bg);
            border: 1px solid color-mix(in srgb, var(--border-color) 70%, transparent);
            cursor: pointer;
            transition: box-shadow 0.28s ease, border-color 0.22s ease, transform 0.22s ease;
            overflow: hidden;
            box-shadow: var(--painel-shadow);
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        }
        .painel-kpi::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: color-mix(in srgb, var(--border-color) 90%, transparent);
        }
        .painel-kpi:hover {
            box-shadow: var(--painel-shadow-hover);
            transform: translateY(-2px);
            border-color: color-mix(in srgb, var(--primary) 18%, var(--border-color));
        }
        .painel-kpi.urgent::before {
            background: color-mix(in srgb, var(--red-500) 70%, transparent);
            height: 2px;
        }
        .painel-kpi.positive::before {
            background: color-mix(in srgb, var(--green-500) 70%, transparent);
        }
        .painel-kpi.warn::before {
            background: color-mix(in srgb, var(--orange-500) 70%, transparent);
        }
        .painel-kpi-label {
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 500;
            order: 1;
            margin-bottom: 10px;
            line-height: 1.35;
        }
        .painel-kpi-value {
            font-size: clamp(1.5rem, 2.5vw, 1.85rem);
            font-weight: 650;
            letter-spacing: -0.04em;
            line-height: 1.05;
            margin: 0;
            color: var(--text-color);
            order: 2;
        }
        .painel-kpi-meta {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 10px;
            order: 3;
            opacity: 0.85;
        }
        .painel-kpi.urgent .painel-kpi-value {
            color: var(--red-600);
        }
        .painel-kpi.positive .painel-kpi-value {
            color: var(--green-700);
        }
        .painel-operacao-grid {
            display: grid;
            grid-template-columns: 1.05fr 0.95fr;
            gap: 24px;
        }
        .painel-panel {
            border-radius: var(--painel-radius);
            border: 1px solid color-mix(in srgb, var(--border-color) 65%, transparent);
            background: var(--card-bg);
            overflow: hidden;
            box-shadow: var(--painel-shadow);
            transition: box-shadow 0.25s ease;
        }
        .painel-panel:hover {
            box-shadow: var(--painel-shadow-hover);
        }
        .painel-panel-head {
            padding: 18px 22px;
            border-bottom: 1px solid color-mix(in srgb, var(--border-color) 50%, transparent);
            font-size: 14px;
            font-weight: 600;
            letter-spacing: -0.01em;
            color: var(--text-color);
            background: color-mix(in srgb, var(--subtle-fg) 40%, var(--card-bg));
        }
        .painel-op-list { padding: 8px 0 12px; }
        .painel-op-item {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            padding: 18px 22px;
            margin: 0 12px 8px;
            border-radius: var(--painel-radius-sm);
            cursor: pointer;
            border: 1px solid transparent;
            border-left: 3px solid transparent;
            transition: background 0.2s ease, border-color 0.2s ease, transform 0.18s ease;
            min-height: 48px;
        }
        .painel-op-item:last-child { margin-bottom: 4px; }
        .painel-op-item:hover {
            background: color-mix(in srgb, var(--subtle-fg) 65%, var(--card-bg));
            border-color: color-mix(in srgb, var(--border-color) 80%, transparent);
            transform: translateX(2px);
        }
        .painel-op-item--hot {
            border-left-color: color-mix(in srgb, var(--red-500) 55%, transparent);
            background: color-mix(in srgb, var(--red-500) 4%, var(--card-bg));
        }
        .painel-op-item--hot:hover {
            background: color-mix(in srgb, var(--red-500) 7%, var(--card-bg));
        }
        .painel-op-time {
            flex-shrink: 0;
            width: 56px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            padding-top: 3px;
            font-variant-numeric: tabular-nums;
        }
        .painel-op-body { flex: 1; min-width: 0; }
        .painel-op-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-color);
            margin: 0 0 5px;
            line-height: 1.4;
            letter-spacing: -0.01em;
        }
        .painel-op-sub {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.45;
        }
        .painel-op-side {
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 8px;
        }
        .painel-op-side .indicator-pill {
            font-size: 11px;
            padding: 3px 10px;
        }
        .painel-finance-grid {
            display: grid;
            grid-template-columns: 1.15fr 1fr;
            gap: 24px;
        }
        .painel-finance-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            padding: 22px;
        }
        .painel-stat {
            padding: 18px 18px 16px;
            border-radius: var(--painel-radius-sm);
            background: color-mix(in srgb, var(--subtle-fg) 50%, var(--card-bg));
            border: 1px solid color-mix(in srgb, var(--border-color) 45%, transparent);
            transition: border-color 0.2s ease;
        }
        .painel-stat:hover {
            border-color: color-mix(in srgb, var(--border-color) 90%, transparent);
        }
        .painel-stat-label {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 10px;
            font-weight: 500;
        }
        .painel-stat-value {
            font-size: 1.25rem;
            font-weight: 650;
            letter-spacing: -0.03em;
            line-height: 1.15;
        }
        .painel-stat-value.danger { color: var(--red-600); }
        .painel-stat-value.success { color: var(--green-700); }
        .painel-chart { padding: 22px 24px 28px; }
        .painel-chart-row {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 18px;
        }
        .painel-chart-row:last-child { margin-bottom: 0; }
        .painel-chart-label {
            width: 96px;
            flex-shrink: 0;
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 500;
        }
        .painel-chart-track {
            flex: 1;
            height: 6px;
            border-radius: 999px;
            background: color-mix(in srgb, var(--subtle-fg) 80%, transparent);
            overflow: hidden;
        }
        .painel-chart-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.7s cubic-bezier(0.22, 1, 0.36, 1);
        }
        .painel-chart-fill.danger {
            background: color-mix(in srgb, var(--red-500) 75%, var(--orange-500));
        }
        .painel-chart-fill.success {
            background: color-mix(in srgb, var(--green-500) 80%, transparent);
        }
        .painel-chart-fill.warning {
            background: color-mix(in srgb, var(--orange-500) 75%, transparent);
        }
        .painel-chart-fill.neutral {
            background: color-mix(in srgb, var(--gray-500) 45%, transparent);
        }
        .painel-chart-amt {
            width: 108px;
            text-align: right;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-color);
            font-variant-numeric: tabular-nums;
        }
        .painel-section--secondary .painel-section-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-muted);
        }
        .painel-secondary-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-bottom: var(--painel-gap);
            align-items: start;
        }
        .painel-section--secondary {
            margin-bottom: 0;
        }
        .painel-section--secondary .painel-panel {
            min-height: 220px;
        }
        .painel-schedule-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 12px 14px 16px;
        }
        .painel-schedule-card {
            display: grid;
            grid-template-columns: 76px minmax(0, 1fr) auto;
            gap: 14px;
            align-items: start;
            padding: 14px 16px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 55%, transparent);
            background: color-mix(in srgb, var(--subtle-fg) 35%, var(--card-bg));
            cursor: pointer;
            transition: background 0.2s ease, border-color 0.2s ease, transform 0.18s ease;
        }
        .painel-schedule-card:hover {
            background: color-mix(in srgb, var(--subtle-fg) 70%, var(--card-bg));
            border-color: color-mix(in srgb, var(--primary) 20%, var(--border-color));
            transform: translateY(-1px);
        }
        .painel-schedule-card--urgent {
            border-left: 3px solid color-mix(in srgb, var(--red-500) 60%, transparent);
            background: color-mix(in srgb, var(--red-500) 5%, var(--card-bg));
        }
        .painel-schedule-card--today {
            border-left: 3px solid color-mix(in srgb, var(--orange-500) 60%, transparent);
        }
        .painel-schedule-when {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 72px;
            padding: 8px 6px;
            border-radius: 10px;
            background: var(--card-bg);
            border: 1px solid color-mix(in srgb, var(--border-color) 50%, transparent);
            text-align: center;
            line-height: 1.2;
        }
        .painel-schedule-day {
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            color: var(--text-color);
            font-variant-numeric: tabular-nums;
        }
        .painel-schedule-month {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-top: 2px;
            letter-spacing: 0.04em;
        }
        .painel-schedule-hour,
        .painel-schedule-countdown {
            font-size: 11px;
            font-weight: 600;
            color: var(--primary);
            margin-top: 6px;
            font-variant-numeric: tabular-nums;
        }
        .painel-schedule-countdown.danger { color: var(--red-600); }
        .painel-schedule-countdown.warn { color: var(--orange-600); }
        .painel-schedule-body { min-width: 0; }
        .painel-schedule-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-color);
            margin: 0 0 6px;
            line-height: 1.35;
            letter-spacing: -0.01em;
            word-break: break-word;
        }
        .painel-schedule-sub {
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.45;
            word-break: break-word;
        }
        .painel-schedule-meta {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 8px;
            flex-shrink: 0;
            max-width: 120px;
        }
        .painel-schedule-meta .indicator-pill {
            font-size: 10px;
            padding: 3px 8px;
            max-width: 110px;
        }
        .painel-section-foot {
            padding: 0 18px 14px;
            text-align: right;
        }
        .painel-section-foot-link {
            font-size: 12px;
            font-weight: 500;
            color: var(--primary);
            cursor: pointer;
        }
        .painel-section-foot-link:hover { opacity: 0.85; }
        .painel-parcela-card {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px 20px;
            padding: 20px 22px;
            margin: 0 12px 10px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid transparent;
            cursor: pointer;
            transition: background 0.2s ease, border-color 0.2s ease;
        }
        .painel-parcela-card:last-child { margin-bottom: 12px; }
        .painel-parcela-card:hover {
            background: color-mix(in srgb, var(--subtle-fg) 55%, var(--card-bg));
            border-color: color-mix(in srgb, var(--border-color) 70%, transparent);
        }
        .painel-parcela-main { flex: 1; min-width: 180px; }
        .painel-parcela-valor {
            font-weight: 650;
            font-size: 15px;
            letter-spacing: -0.03em;
        }
        .painel-btn-recebida {
            min-height: 36px;
            padding: 8px 14px;
            border-radius: var(--painel-radius-sm);
            font-size: 12px;
            font-weight: 600;
            border: 1px solid color-mix(in srgb, var(--green-500) 25%, transparent);
            background: color-mix(in srgb, var(--green-500) 12%, var(--card-bg));
            color: var(--green-700);
            cursor: pointer;
            transition: background 0.18s ease, transform 0.15s ease;
        }
        .painel-btn-recebida:hover {
            background: color-mix(in srgb, var(--green-500) 20%, var(--card-bg));
            transform: scale(1.02);
        }
        .painel-btn-entrar {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            min-height: 36px;
            padding: 8px 14px;
            border-radius: var(--painel-radius-sm);
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            white-space: nowrap;
            border: 1px solid color-mix(in srgb, var(--primary) 28%, transparent);
            background: color-mix(in srgb, var(--primary) 12%, var(--card-bg));
            color: var(--primary);
            transition: background 0.18s ease, border-color 0.18s ease, transform 0.15s ease;
        }
        .painel-btn-entrar:hover {
            background: color-mix(in srgb, var(--primary) 20%, var(--card-bg));
            border-color: color-mix(in srgb, var(--primary) 42%, transparent);
            color: var(--primary);
            transform: scale(1.02);
        }
        .painel-btn-entrar--muted {
            cursor: default;
            opacity: 0.72;
            border-color: var(--border-color);
            background: var(--bg-subtle);
            color: var(--text-muted);
        }
        .painel-btn-entrar--muted:hover {
            transform: none;
            background: var(--bg-subtle);
            border-color: var(--border-color);
            color: var(--text-muted);
        }
        .painel-empty {
            padding: 48px 28px 52px;
            text-align: center;
            color: var(--text-muted);
        }
        .painel-empty-icon {
            display: flex;
            justify-content: center;
            margin-bottom: 16px;
            opacity: 0.45;
            color: var(--text-muted);
        }
        .painel-empty-title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-color);
            margin: 0 0 8px;
            letter-spacing: -0.01em;
        }
        .painel-empty-hint {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
            max-width: 280px;
            margin: 0 auto;
        }
        .painel-muted {
            color: var(--text-muted);
            font-size: 13px;
            white-space: nowrap;
        }
        .painel-skeleton-hero {
            height: 100px;
            border-radius: var(--painel-radius);
            margin-bottom: 24px;
            background: linear-gradient(90deg, var(--subtle-fg) 25%, var(--gray-100) 50%, var(--subtle-fg) 75%);
            background-size: 200% 100%;
            animation: painel-shimmer 1.4s ease infinite;
        }
        .painel-skeleton-kpis {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .painel-skeleton-kpi {
            height: 110px;
            border-radius: var(--painel-radius);
            background: linear-gradient(90deg, var(--subtle-fg) 25%, var(--gray-100) 50%, var(--subtle-fg) 75%);
            background-size: 200% 100%;
            animation: painel-shimmer 1.4s ease infinite;
        }
        .painel-skeleton-panel {
            height: 280px;
            border-radius: var(--painel-radius);
            margin-bottom: 16px;
            background: linear-gradient(90deg, var(--subtle-fg) 25%, var(--gray-100) 50%, var(--subtle-fg) 75%);
            background-size: 200% 100%;
            animation: painel-shimmer 1.4s ease infinite;
        }
        @keyframes painel-shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        @media (max-width: 1024px) {
            .painel-root { padding: 8px 20px 48px; }
            .painel-kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; }
            .painel-operacao-grid, .painel-finance-grid, .painel-secondary-grid { grid-template-columns: 1fr; }
            .painel-parcela-main { min-width: 100%; }
        }
        @media (max-width: 768px) {
            .painel-root {
                padding: 0 12px 72px;
                --painel-gap: 28px;
                --painel-gap-md: 20px;
                max-width: none;
            }
            .painel-hero {
                padding: 16px 0 18px;
                margin-bottom: var(--painel-gap-md);
            }
            .painel-hero-greeting {
                font-size: 1.35rem;
            }
            .painel-hero-context {
                font-size: 13px;
                line-height: 1.5;
            }
            .painel-hero-pulse {
                flex-direction: column;
                align-items: stretch;
                gap: 12px;
            }
            .painel-hero-pulse-stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px 12px;
            }
            .painel-hero-pulse-stats > span,
            .painel-hero-pulse-stats > .painel-hero-stat {
                display: block;
                padding: 10px 12px;
                border-radius: var(--painel-radius-sm);
                background: color-mix(in srgb, var(--subtle-fg) 55%, var(--card-bg));
                border: 1px solid color-mix(in srgb, var(--border-color) 55%, transparent);
                font-size: 12px;
                line-height: 1.35;
                white-space: normal;
            }
            .painel-hero-stat--money {
                white-space: normal;
                grid-column: 1 / -1;
            }
            .painel-hero-stat--money .painel-hero-money {
                white-space: nowrap;
            }
            .painel-hero-pulse .dot { display: none; }
            .painel-urgency-badge {
                align-self: stretch;
                justify-content: center;
                text-align: center;
            }
            .painel-actions-label { display: block; }
            .painel-actions-wrap {
                margin-left: -12px;
                margin-right: -12px;
                margin-bottom: var(--painel-gap-md);
            }
            .painel-actions-label {
                padding: 0 12px;
            }
            .painel-actions {
                flex-wrap: nowrap;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scroll-snap-type: x proximity;
                gap: 8px;
                padding: 0 12px 6px;
                scrollbar-width: none;
            }
            .painel-actions::-webkit-scrollbar { display: none; }
            .painel-action-chip {
                flex: 0 0 auto;
                scroll-snap-align: start;
                min-width: 96px;
                max-width: 112px;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 12px 8px;
                text-align: center;
                font-size: 11px;
                line-height: 1.25;
                min-height: 84px;
            }
            .painel-action-chip .icon {
                width: 18px;
                height: 18px;
            }
            .painel-action-chip span {
                white-space: normal;
                display: block;
            }
            .painel-section-head {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }
            .painel-section-link {
                white-space: normal;
            }
            .painel-periodo-bar {
                flex-direction: column;
                align-items: stretch;
                gap: 14px;
            }
            .painel-filtro-group {
                flex-direction: column;
                align-items: stretch;
            }
            .painel-periodo-filters,
            .painel-linhas-filters {
                width: 100%;
            }
            .painel-periodo-btn,
            .painel-linhas-btn {
                flex: 1;
                min-width: 0;
                text-align: center;
            }
            .painel-kpi-grid { grid-template-columns: 1fr; gap: 12px; }
            .painel-kpi {
                min-height: 92px;
                padding: 18px 16px 16px;
            }
            .painel-kpi-value {
                font-size: 1.45rem;
            }
            .painel-finance-stats { grid-template-columns: 1fr; }
            .painel-op-item, .painel-parcela-card {
                margin-left: 8px;
                margin-right: 8px;
                padding-left: 14px;
                padding-right: 14px;
            }
            .painel-op-item {
                flex-wrap: wrap;
            }
            .painel-op-side {
                width: 100%;
                flex-direction: row;
                align-items: center;
                justify-content: flex-start;
                margin-top: 4px;
            }
            .painel-parcela-card {
                flex-direction: column;
                align-items: stretch;
            }
            .painel-parcela-card .painel-btn-recebida,
            .painel-parcela-card .painel-btn-entrar {
                width: 100%;
                justify-content: center;
            }
            .painel-secondary-grid { grid-template-columns: 1fr; }
            .painel-schedule-card {
                grid-template-columns: 56px minmax(0, 1fr);
                grid-template-rows: auto auto;
                padding: 14px 12px;
            }
            .painel-schedule-meta {
                grid-column: 1 / -1;
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: flex-start;
                max-width: none;
            }
            .painel-chart-label { width: 64px; font-size: 11px; }
            .painel-chart-amt { width: 76px; font-size: 12px; }
        }
        @media (max-width: 640px) {
            .painel-root { padding: 0 12px 64px; }
            .painel-hero-pulse-stats {
                grid-template-columns: 1fr;
            }
        }
        .painel-periodo-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px 20px;
            margin-bottom: var(--painel-gap-md);
            padding: 16px 20px;
            border-radius: var(--painel-radius);
            border: 1px solid color-mix(in srgb, var(--primary) 18%, var(--border-color));
            background: linear-gradient(
                135deg,
                color-mix(in srgb, var(--primary) 6%, var(--card-bg)) 0%,
                var(--card-bg) 100%
            );
            box-shadow: var(--painel-shadow);
        }
        .painel-periodo-bar .painel-filtro-group {
            width: 100%;
            justify-content: space-between;
        }
        .painel-periodo-label {
            font-size: 13px;
            font-weight: 700;
            letter-spacing: -0.01em;
            color: var(--text-color);
        }
        .painel-periodo-filters {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            padding: 4px;
            border-radius: 10px;
            background: color-mix(in srgb, var(--subtle-fg) 55%, var(--card-bg));
            border: 1px solid color-mix(in srgb, var(--border-color) 60%, transparent);
        }
        .painel-periodo-btn {
            min-height: 36px;
            padding: 8px 16px;
            font-weight: 600;
        }
        .painel-zona-critica {
            margin-bottom: calc(var(--painel-gap) + 4px);
        }
        .painel-destaques-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        @media (min-width: 900px) {
            .painel-destaques-grid { grid-template-columns: 1.2fr 0.8fr; }
        }
        .painel-priority-max { margin-bottom: var(--painel-gap); }
        .painel-priority-high { margin-bottom: var(--painel-gap); }
        .painel-priority-medium { margin-bottom: var(--painel-gap-md); }
        .painel-priority-low {
            margin-bottom: var(--painel-gap-md);
            opacity: 0.98;
        }
        .painel-priority-low .painel-section-title {
            font-size: 0.98rem;
            color: var(--text-muted);
        }
        .painel-zona-secundaria {
            padding-top: 8px;
            border-top: 1px solid color-mix(in srgb, var(--border-color) 45%, transparent);
        }
        .painel-centro-atencao {
            margin-bottom: 0;
        }
        .painel-centro-shell {
            padding: 28px 24px 24px;
            border-radius: calc(var(--painel-radius) + 2px);
            border: 1px solid color-mix(in srgb, var(--primary) 22%, var(--border-color));
            background: linear-gradient(
                165deg,
                color-mix(in srgb, var(--primary) 7%, var(--card-bg)) 0%,
                var(--card-bg) 42%,
                color-mix(in srgb, var(--subtle-fg) 35%, var(--card-bg)) 100%
            );
            box-shadow: var(--painel-shadow-hover);
        }
        .painel-centro-head .painel-section-title {
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.03em;
        }
        .painel-centro-head .painel-section-sub {
            font-size: 14px;
            color: color-mix(in srgb, var(--text-muted) 85%, var(--text-color));
        }
        .painel-prox-audiencia,
        .painel-saude-card {
            border-radius: var(--painel-radius);
            border: 1px solid color-mix(in srgb, var(--border-color) 70%, transparent);
            background: var(--card-bg);
            box-shadow: var(--painel-shadow);
            overflow: hidden;
            transition: box-shadow 0.25s ease, transform 0.2s ease;
        }
        .painel-prox-audiencia:hover,
        .painel-saude-card:hover {
            box-shadow: var(--painel-shadow-hover);
        }
        .painel-prox-audiencia-head,
        .painel-saude-head {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 18px 22px 14px;
            border-bottom: 1px solid color-mix(in srgb, var(--border-color) 45%, transparent);
            background: color-mix(in srgb, var(--subtle-fg) 40%, var(--card-bg));
        }
        .painel-prox-badge,
        .painel-saude-badge {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: color-mix(in srgb, var(--blue-500) 12%, var(--card-bg));
            color: var(--blue-600);
        }
        .painel-saude-badge.tone-green { background: color-mix(in srgb, var(--green-500) 12%, var(--card-bg)); color: var(--green-700); }
        .painel-saude-badge.tone-orange { background: color-mix(in srgb, var(--orange-500) 12%, var(--card-bg)); color: var(--orange-600); }
        .painel-saude-badge.tone-red { background: color-mix(in srgb, var(--red-500) 12%, var(--card-bg)); color: var(--red-600); }
        .painel-prox-title,
        .painel-saude-title {
            margin: 0;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text-color);
        }
        .painel-prox-body {
            padding: 20px 22px 22px;
            cursor: pointer;
        }
        .painel-prox-body:hover {
            background: color-mix(in srgb, var(--subtle-fg) 35%, var(--card-bg));
        }
        .painel-prox-list {
            display: flex;
            flex-direction: column;
        }
        .painel-prox-card {
            padding: 18px 22px 20px;
            cursor: pointer;
            transition: background 0.18s ease;
        }
        .painel-prox-card + .painel-prox-card {
            border-top: 1px solid color-mix(in srgb, var(--border-color) 50%, transparent);
        }
        .painel-prox-card:hover {
            background: color-mix(in srgb, var(--subtle-fg) 35%, var(--card-bg));
        }
        .painel-prox-card-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 8px;
        }
        .painel-prox-mod {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            white-space: nowrap;
            border: 1px solid transparent;
        }
        .painel-prox-mod--presencial {
            color: var(--gray-700);
            background: color-mix(in srgb, var(--gray-500) 12%, var(--card-bg));
            border-color: color-mix(in srgb, var(--gray-500) 22%, transparent);
        }
        .painel-prox-mod--virtual {
            color: var(--blue-700);
            background: color-mix(in srgb, var(--blue-500) 14%, var(--card-bg));
            border-color: color-mix(in srgb, var(--blue-500) 28%, transparent);
        }
        .painel-prox-mod--hibrida {
            color: var(--orange-700);
            background: color-mix(in srgb, var(--orange-500) 14%, var(--card-bg));
            border-color: color-mix(in srgb, var(--orange-500) 28%, transparent);
        }
        .painel-prox-actions {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-top: 14px;
            padding-top: 14px;
            border-top: 1px solid color-mix(in srgb, var(--border-color) 45%, transparent);
        }
        .painel-prox-ordem {
            font-size: 0.85em;
            font-weight: 600;
            color: var(--text-muted);
        }
        .painel-prox-local-hint {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.35;
        }
        .painel-prox-when {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            color: var(--text-color);
            line-height: 1.2;
            flex: 1;
            min-width: 0;
        }
        .painel-prox-tipo {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 12px;
        }
        .painel-prox-meta {
            display: grid;
            gap: 8px;
        }
        .painel-prox-row {
            display: flex;
            align-items: baseline;
            gap: 10px;
            font-size: 13px;
            line-height: 1.4;
        }
        .painel-prox-row-label {
            min-width: 72px;
            font-weight: 600;
            color: var(--text-muted);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .painel-prox-row-value {
            color: var(--text-color);
            font-weight: 500;
        }
        .painel-prox-empty {
            padding: 28px 22px;
            text-align: center;
            color: var(--text-muted);
            font-size: 14px;
        }
        .painel-saude-body {
            padding: 18px 22px 22px;
        }
        .painel-saude-score-wrap {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 18px;
        }
        .painel-saude-ring {
            position: relative;
            width: 88px;
            height: 88px;
            flex-shrink: 0;
        }
        .painel-saude-ring svg {
            width: 88px;
            height: 88px;
            transform: rotate(-90deg);
        }
        .painel-saude-ring-bg {
            fill: none;
            stroke: color-mix(in srgb, var(--border-color) 80%, transparent);
            stroke-width: 8;
        }
        .painel-saude-ring-fill {
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
            transition: stroke-dashoffset 0.6s ease;
        }
        .painel-saude-ring-fill.tone-green { stroke: var(--green-600); }
        .painel-saude-ring-fill.tone-blue { stroke: var(--blue-600); }
        .painel-saude-ring-fill.tone-orange { stroke: var(--orange-600); }
        .painel-saude-ring-fill.tone-red { stroke: var(--red-600); }
        .painel-saude-score-text {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            line-height: 1.1;
        }
        .painel-saude-score-num {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.04em;
        }
        .painel-saude-score-label {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            margin-top: 2px;
        }
        .painel-saude-summary {
            flex: 1;
            min-width: 0;
        }
        .painel-saude-summary h4 {
            margin: 0 0 4px;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .painel-saude-summary p {
            margin: 0;
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.45;
        }
        .painel-saude-rows {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .painel-saude-row {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13px;
            line-height: 1.35;
        }
        .painel-saude-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .painel-saude-dot.red { background: var(--red-500); }
        .painel-saude-dot.orange { background: var(--orange-500); }
        .painel-saude-dot.green { background: var(--green-500); }
        .painel-saude-row strong {
            font-weight: 700;
            color: var(--text-color);
        }
        .painel-success-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 36px 24px;
            border-radius: var(--painel-radius-sm);
            background: color-mix(in srgb, var(--green-500) 8%, var(--card-bg));
            border: 1px solid color-mix(in srgb, var(--green-500) 22%, transparent);
        }
        .painel-success-icon {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: color-mix(in srgb, var(--green-500) 15%, var(--card-bg));
            color: var(--green-700);
            margin-bottom: 12px;
        }
        .painel-success-title {
            margin: 0;
            font-size: 15px;
            font-weight: 700;
            color: var(--green-700);
        }
        .painel-success-hint {
            margin: 8px 0 0;
            font-size: 13px;
            color: var(--text-muted);
            max-width: 28rem;
            line-height: 1.45;
        }
        .painel-com-item {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 12px 16px;
            align-items: center;
            padding: 16px 18px;
            margin: 0 8px 10px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 55%, transparent);
            background: color-mix(in srgb, var(--subtle-fg) 25%, var(--card-bg));
            cursor: pointer;
            transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.18s ease;
        }
        .painel-com-item:last-child { margin-bottom: 4px; }
        .painel-com-item:hover {
            background: color-mix(in srgb, var(--subtle-fg) 55%, var(--card-bg));
            border-color: color-mix(in srgb, var(--primary) 18%, var(--border-color));
            box-shadow: var(--painel-shadow);
            transform: translateY(-1px);
        }
        .painel-com-cliente {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-muted);
            margin-bottom: 4px;
        }
        .painel-com-assunto {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-color);
            line-height: 1.35;
            margin-bottom: 4px;
        }
        .painel-com-meta {
            font-size: 12px;
            color: var(--text-muted);
        }
        .painel-com-side {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 8px;
        }
        .painel-com-dias {
            font-size: 12px;
            font-weight: 600;
            color: var(--orange-600);
            font-variant-numeric: tabular-nums;
        }
        .painel-finance-donut-wrap {
            padding: 16px 20px 24px;
            min-height: 240px;
        }
        .painel-finance-donut-wrap .graph-svg-tip {
            z-index: 10;
        }
        .painel-list-item {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 8px 16px;
            align-items: center;
            padding: 16px 18px;
            margin: 0 10px 10px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 50%, transparent);
            background: var(--card-bg);
            transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .painel-list-item:last-child { margin-bottom: 12px; }
        .painel-list-item:hover {
            background: color-mix(in srgb, var(--subtle-fg) 45%, var(--card-bg));
            border-color: color-mix(in srgb, var(--primary) 15%, var(--border-color));
            box-shadow: var(--painel-shadow);
        }
        .painel-list-valor {
            font-size: 15px;
            font-weight: 700;
            letter-spacing: -0.02em;
            text-align: right;
        }
        .painel-list-valor.danger { color: var(--red-600); }
        .painel-list-valor.warn { color: var(--orange-600); }
        .painel-schedule-item {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 12px 16px;
            align-items: center;
            padding: 16px 18px;
            margin: 0 8px 10px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 50%, transparent);
            background: color-mix(in srgb, var(--subtle-fg) 20%, var(--card-bg));
            cursor: pointer;
            transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .painel-schedule-item:last-child { margin-bottom: 4px; }
        .painel-list-side {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 8px;
        }
        .painel-panel-head--sub {
            border-top: 1px solid color-mix(in srgb, var(--border-color) 50%, transparent);
            font-size: 13px;
        }
        .painel-chart--percent {
            padding-top: 12px;
        }
        .painel-atencao-card.tone-gray { border-left: 5px solid var(--painel-tone-gray); }
        .painel-filtro-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px 12px;
        }
        .painel-linhas-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            white-space: nowrap;
        }
        .painel-periodo-filters,
        .painel-linhas-filters {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .painel-periodo-btn,
        .painel-linhas-btn {
            min-height: 36px;
            padding: 6px 14px;
            border-radius: 999px;
            border: 1px solid color-mix(in srgb, var(--border-color) 80%, transparent);
            background: var(--card-bg);
            color: var(--text-muted);
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .painel-periodo-btn.active,
        .painel-linhas-btn.active {
            background: color-mix(in srgb, var(--primary) 12%, var(--card-bg));
            border-color: color-mix(in srgb, var(--primary) 35%, var(--border-color));
            color: var(--primary);
            font-weight: 600;
        }
        .painel-linhas-filters--inline {
            gap: 4px;
        }
        .painel-linhas-filters--inline .painel-linhas-btn {
            min-width: 32px;
            min-height: 28px;
            padding: 2px 8px;
            font-size: 11px;
        }
        .painel-list-meta {
            font-size: 11px;
            font-weight: 500;
            color: var(--text-muted);
            white-space: nowrap;
        }
        .painel-section-head-actions {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }
        .painel-centro-atencao {
            margin-bottom: 0;
        }
        .painel-centro-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        @media (min-width: 640px) {
            .painel-centro-grid { grid-template-columns: repeat(3, 1fr); }
        }
        @media (min-width: 1024px) {
            .painel-centro-grid { grid-template-columns: repeat(3, 1fr); }
        }
        .painel-centro-groups {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .painel-centro-group-title {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin: 0 0 10px;
        }
        .painel-duo-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: var(--painel-gap-sm);
            margin-bottom: var(--painel-gap);
        }
        @media (min-width: 768px) {
            .painel-duo-grid { grid-template-columns: 1fr 1fr; }
        }
        .painel-duo-grid .painel-section {
            margin-bottom: 0;
        }
        .painel-section--nested {
            margin-bottom: var(--painel-gap-sm);
        }
        .painel-section--nested .painel-section-head {
            margin-bottom: 12px;
        }
        .painel-section--nested .painel-section-title {
            font-size: 0.95rem;
        }
        .painel-horas-panel {
            padding: 18px 20px;
        }
        .painel-atencao-card {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px 16px 14px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 65%, transparent);
            background: var(--card-bg);
            box-shadow: var(--painel-shadow);
            cursor: pointer;
            transition: transform 0.18s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            min-height: 88px;
        }
        .painel-atencao-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--painel-shadow-hover);
            border-color: color-mix(in srgb, var(--primary) 20%, var(--border-color));
        }
        .painel-atencao-card.tone-red { border-left: 5px solid var(--painel-tone-red); }
        .painel-atencao-card.tone-orange { border-left: 5px solid var(--painel-tone-orange); }
        .painel-atencao-card.tone-yellow { border-left: 5px solid var(--painel-tone-yellow); }
        .painel-atencao-card.tone-green { border-left: 5px solid var(--painel-tone-green); }
        .painel-atencao-card.tone-blue { border-left: 5px solid var(--painel-tone-blue); }
        .painel-atencao-card.tone-gray { border-left: 5px solid var(--painel-tone-gray); }
        .painel-atencao-icon {
            flex-shrink: 0;
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: color-mix(in srgb, var(--subtle-fg) 60%, var(--card-bg));
        }
        .painel-atencao-body { flex: 1; min-width: 0; }
        .painel-atencao-count {
            font-size: clamp(1.35rem, 2vw, 1.65rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.05;
            color: var(--text-color);
        }
        .painel-atencao-label {
            font-size: 12px;
            font-weight: 500;
            color: var(--text-muted);
            margin-top: 6px;
            line-height: 1.35;
            white-space: normal;
            word-break: break-word;
        }
        .painel-atencao-meta {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            margin-top: 4px;
            line-height: 1.25;
            opacity: 0.95;
        }
        .painel-timeline-modern {
            position: relative;
            padding: 20px 24px 24px 56px;
        }
        .painel-tl-item {
            position: relative;
            padding: 0 0 28px 0;
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 8px 12px;
            align-items: start;
            cursor: pointer;
        }
        .painel-tl-item:last-child { padding-bottom: 0; }
        .painel-tl-item:not(:last-child)::before {
            content: "";
            position: absolute;
            left: -29px;
            top: 22px;
            bottom: 4px;
            width: 2px;
            background: color-mix(in srgb, var(--border-color) 85%, transparent);
        }
        .painel-tl-marker {
            position: absolute;
            left: -36px;
            top: 6px;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 3px solid var(--card-bg);
            box-shadow: 0 0 0 2px currentColor;
            z-index: 1;
        }
        .painel-tl-item.tone-red .painel-tl-marker { color: var(--red-500); background: var(--red-500); }
        .painel-tl-item.tone-orange .painel-tl-marker { color: var(--orange-500); background: var(--orange-500); }
        .painel-tl-item.tone-yellow .painel-tl-marker { color: var(--yellow-500); background: var(--yellow-500); }
        .painel-tl-item.tone-blue .painel-tl-marker { color: var(--blue-500); background: var(--blue-500); }
        .painel-tl-item.tone-gray .painel-tl-marker { color: var(--gray-500); background: var(--gray-500); }
        .painel-tl-item:hover .painel-tl-content {
            background: color-mix(in srgb, var(--subtle-fg) 50%, var(--card-bg));
        }
        .painel-tl-content {
            padding: 12px 14px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid transparent;
            transition: background 0.18s ease, border-color 0.18s ease;
        }
        .painel-tl-item:hover .painel-tl-content {
            border-color: color-mix(in srgb, var(--border-color) 60%, transparent);
        }
        .painel-tl-when {
            font-size: 13px;
            font-weight: 700;
            color: var(--text-color);
            margin-bottom: 6px;
            letter-spacing: -0.01em;
        }
        .painel-tl-type {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        .painel-tl-item.tone-red .painel-tl-type { color: var(--red-600); }
        .painel-tl-item.tone-orange .painel-tl-type { color: var(--orange-600); }
        .painel-tl-item.tone-yellow .painel-tl-type { color: var(--yellow-700); }
        .painel-tl-item.tone-blue .painel-tl-type { color: var(--blue-600); }
        .painel-tl-item.tone-gray .painel-tl-type { color: var(--gray-600); }
        .painel-tl-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-color);
            line-height: 1.35;
            word-break: break-word;
        }
        .painel-tl-sub {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
            line-height: 1.4;
            word-break: break-word;
        }
        .painel-timeline-list {
            display: none;
        }
        .painel-kpi-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 16px;
        }
        .painel-kpi-row:last-child { margin-bottom: 0; }
        @media (max-width: 1024px) {
            .painel-kpi-row { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 640px) {
            .painel-kpi-row { grid-template-columns: 1fr; }
            .painel-centro-grid { grid-template-columns: 1fr; }
            .painel-centro-shell { padding: 20px 16px 18px; }
            .painel-timeline-modern { padding-left: 48px; }
            .painel-tl-item { grid-template-columns: 1fr; }
            .painel-tl-item .indicator-pill { justify-self: start; }
        }
    `;
    $('<style id="painel-advocacia-styles">' + css + "</style>").appendTo("head");
}

var PAINEL_LIST_LIMIT_KEYS = [
    "timeline",
    "comunicacoes",
    "parcelas",
    "despesas",
    "custas",
];

function painel_default_list_limits() {
    return {
        timeline: 5,
        comunicacoes: 5,
        parcelas: 5,
        despesas: 5,
        custas: 5,
    };
}

function painel_merge_list_limits(page) {
    var defaults = painel_default_list_limits();
    var current = (page && page.painel_list_limits) || {};
    var merged = {};
    PAINEL_LIST_LIMIT_KEYS.forEach(function (key) {
        merged[key] = current[key] != null ? cint(current[key]) : defaults[key];
    });
    return merged;
}

function render_list_limit_controls(list_key, current_limit) {
    var opcoes = [
        { val: 5, label: "5" },
        { val: 10, label: "10" },
        { val: 15, label: "15" },
        { val: 0, label: __("Todos") },
    ];
    current_limit = current_limit != null ? cint(current_limit) : 5;
    var h =
        '<div class="painel-linhas-filters painel-linhas-filters--inline" title="' +
        __("Itens nesta lista") +
        '">';
    opcoes.forEach(function (op) {
        h +=
            '<button type="button" class="painel-linhas-btn' +
            (current_limit === op.val ? " active" : "") +
            '" data-list="' +
            list_key +
            '" data-linhas="' +
            op.val +
            '">' +
            op.label +
            "</button>";
    });
    h += "</div>";
    return h;
}

function load_painel(page) {
    mostrar_skeleton(page.painel_container);
    var periodo = page.painel_periodo || 7;
    var list_limits = painel_merge_list_limits(page);
    frappe.xcall("advocacia.advocacia.painel_api.get_painel_data", {
        periodo_dias: periodo,
        list_limits: list_limits,
    })
        .then(function (data) {
            page.painel_data = data;
            render_painel(page.painel_container, data, page);
        })
        .catch(function (err) {
            handle_error(page.painel_container, err);
        });
}

function mostrar_skeleton($container) {
    var html =
        '<div class="painel-skeleton-hero"></div>' +
        '<div class="painel-skeleton-kpis">' +
        '<div class="painel-skeleton-kpi"></div><div class="painel-skeleton-kpi"></div><div class="painel-skeleton-kpi"></div>' +
        "</div>" +
        '<div class="painel-skeleton-panel"></div><div class="painel-skeleton-panel"></div>';
    $container.html(html);
}

function handle_error($container, err) {
    var msg = (err && err.message) || String(err);
    $container.html(
        '<div class="painel-panel"><div class="painel-empty" style="color: var(--red-500);">' +
            __("Erro ao carregar o painel: {0}", [msg]) +
            "</div></div>"
    );
}

function painel_periodo_fim(page) {
    var dias = (page && page.painel_periodo) || 7;
    return frappe.datetime.add_days(frappe.datetime.get_today(), dias);
}

function painel_periodo_label(dias) {
    dias = cint(dias) || 7;
    if (dias === 1) return __("hoje");
    if (dias === 7) return __("7 dias");
    if (dias === 15) return __("15 dias");
    if (dias === 30) return __("30 dias");
    return __("{0} dias", [dias]);
}

function painel_periodo_previsto_label(dias) {
    dias = cint(dias) || 7;
    if (dias === 1) return __("previsto hoje");
    if (dias === 7) return __("previsto em 7 dias");
    if (dias === 15) return __("previsto em 15 dias");
    if (dias === 30) return __("previsto em 30 dias");
    return __("previsto em {0} dias", [dias]);
}

function painel_periodo_a_receber_label(dias) {
    dias = cint(dias) || 7;
    if (dias === 1) return __("A receber hoje");
    return __("A receber ({0})", [painel_periodo_label(dias)]);
}

function painel_periodo_recebidos_label(dias) {
    dias = cint(dias) || 7;
    if (dias === 1) return __("Recebidos hoje");
    return __("Recebidos ({0})", [painel_periodo_label(dias)]);
}

function painel_periodo_enunciado(dias) {
    dias = cint(dias) || 7;
    if (dias === 1) return __("hoje");
    return __("nos próximos {0} dias", [dias]);
}

function painel_periodo_scope_label(dias) {
    dias = cint(dias) || 7;
    if (dias === 1) return __("Período: hoje");
    return __("Período: {0} dias", [dias]);
}

function painel_horas_label(dias) {
    dias = cint(dias) || 7;
    if (dias === 1) return __("Horas hoje");
    return __("Horas ({0})", [painel_periodo_label(dias)]);
}

function painel_list_meta_html(meta, list_limit) {
    if (!meta || !meta.total) return "";
    if (!list_limit || list_limit === 0 || meta.showing >= meta.total) {
        return (
            '<span class="painel-list-meta">' +
            __("Todos ({0})", [meta.total]) +
            "</span>"
        );
    }
    return (
        '<span class="painel-list-meta">' +
        __("{0} de {1}", [meta.showing, meta.total]) +
        "</span>"
    );
}

function painel_goto_list(doctype, filters) {
    advocacia.list_nav.goto(doctype, filters || []);
}

function render_painel($container, d, page) {
    var periodo = d.periodo_dias || page.painel_periodo || 7;
    var limits = d.list_limits || painel_merge_list_limits(page);
    var meta = d.list_meta || {};
    var horas = d.horas_periodo != null ? d.horas_periodo : d.horas_semana;
    page.painel_list_limits = limits;
    var html = '<div class="painel-content">';
    html += render_header(d.resumo, d.kpis, periodo, d.financeiro);
    html += render_filtros_painel(periodo);
    html += render_acoes_rapidas();
    html += '<div class="painel-zona-critica">';
    html += render_centro_atencao(
        d.centro_atencao,
        d.kpis,
        d.financeiro,
        horas,
        d.total_despesas_mes,
        periodo
    );
    html += '<div class="painel-destaques-grid">';
    html += render_proxima_audiencia(d.audiencias, d.timeline);
    html += render_saude_operacional(d.centro_atencao, d.kpis, d.financeiro);
    html += "</div></div>";
    html += render_timeline(d.timeline, periodo, meta.timeline, limits.timeline);
    html += render_comunicacoes_pendentes(
        d.comunicacoes_pendentes || d.ultimas_comunicacoes,
        periodo,
        meta.comunicacoes,
        limits.comunicacoes
    );
    html += render_indicadores_painel(
        d.centro_atencao,
        d.kpis,
        d.financeiro,
        horas,
        d.total_despesas_mes,
        periodo
    );
    html += '<div class="painel-zona-secundaria">';
    html += render_financeiro(d.financeiro, periodo);
    html += render_duo_honorarios_despesas(
        d.parcelas,
        d.despesas_pendentes,
        d.total_despesas_mes,
        meta.parcelas,
        meta.despesas,
        limits.parcelas,
        limits.despesas
    );
    html += render_duo_custas_horas(
        d.custas_pendentes_repasse,
        d.total_custas_mes,
        horas,
        meta.custas,
        periodo,
        limits.custas
    );
    html += "</div>";
    html += "</div>";
    $container.html(html);
    bind_painel_filters($container, page);
    bind_atencao_routes($container, page);
    painel_init_finance_chart($container, d.financeiro, page);
}

function render_success_state(title, hint) {
    return (
        '<div class="painel-success-state">' +
        '<div class="painel-success-icon">' +
        painel_icon("check-circle") +
        "</div>" +
        '<p class="painel-success-title">' +
        frappe.utils.escape_html(title) +
        "</p>" +
        (hint
            ? '<p class="painel-success-hint">' + frappe.utils.escape_html(hint) + "</p>"
            : "") +
        "</div>"
    );
}

function render_empty_state(icon, title, hint) {
    return (
        '<div class="painel-empty">' +
        '<div class="painel-empty-icon">' +
        painel_icon(icon || "inbox") +
        "</div>" +
        '<p class="painel-empty-title">' +
        frappe.utils.escape_html(title) +
        "</p>" +
        (hint
            ? '<p class="painel-empty-hint">' + frappe.utils.escape_html(hint) + "</p>"
            : "") +
        "</div>"
    );
}

function painel_context_html(resumo, kpis, periodo_dias, financeiro) {
    resumo = resumo || {};
    kpis = kpis || {};
    financeiro = financeiro || {};
    periodo_dias = cint(periodo_dias) || 7;

    function part(text) {
        return (
            '<span class="painel-hero-context-part">' +
            frappe.utils.escape_html(text) +
            "</span>"
        );
    }

    function money_part(label, value) {
        return (
            '<span class="painel-hero-context-part">' +
            frappe.utils.escape_html(label + ": ") +
            '<span class="painel-hero-money">' +
            frappe.utils.escape_html(fmt_currency(value, true)) +
            "</span></span>"
        );
    }

    if (resumo.urgencia !== "alta") {
        return part(
            __("Visão operacional {0} — nenhuma urgência crítica no radar.", [
                painel_periodo_enunciado(periodo_dias),
            ])
        );
    }

    var chunks = [];
    if (resumo.audiencias_hoje) {
        chunks.push(
            part(
                __("{0} audiência(s) hoje exigem presença ou preparo", [resumo.audiencias_hoje])
            )
        );
    }
    if (resumo.parcelas_vencidas) {
        chunks.push(
            part(__("{0} parcela(s) vencida(s) aguardam recebimento", [resumo.parcelas_vencidas]))
        );
    }
    if (resumo.prazos_urgentes) {
        chunks.push(
            part(__("{0} prazo(s) com vencimento iminente", [resumo.prazos_urgentes]))
        );
    }
    var previsto =
        (financeiro.previsto_periodo && financeiro.previsto_periodo.valor) ||
        resumo.previsto_periodo_valor ||
        0;
    if (previsto) {
        chunks.push(money_part(painel_periodo_previsto_label(periodo_dias), previsto));
    }
    return chunks.join("");
}

function painel_greeting() {
    var h = new Date().getHours();
    if (h < 12) return __("Bom dia");
    if (h < 18) return __("Boa tarde");
    return __("Boa noite");
}

function render_header(resumo, kpis, periodo_dias, financeiro) {
    resumo = resumo || {};
    kpis = kpis || {};
    financeiro = financeiro || {};
    periodo_dias = cint(periodo_dias) || 7;
    var urg = resumo.urgencia === "alta" ? "alta" : "normal";
    var previsto_val =
        resumo.previsto_periodo_valor != null
            ? resumo.previsto_periodo_valor
            : resumo.previsto_semana_valor ||
              (financeiro.previsto_periodo && financeiro.previsto_periodo.valor) ||
              (financeiro.previsto_semana && financeiro.previsto_semana.valor) ||
              0;
    var pulse_stats =
        '<div class="painel-hero-pulse-stats">' +
        '<span class="painel-hero-stat"><strong>' +
        (resumo.audiencias_hoje || 0) +
        "</strong> " +
        __("audiência(s) hoje") +
        "</span>";
    if (resumo.prazos_urgentes) {
        pulse_stats +=
            '<span class="painel-hero-stat"><strong>' +
            resumo.prazos_urgentes +
            "</strong> " +
            __("prazo(s) crítico(s)") +
            "</span>";
    }
    pulse_stats +=
        '<span class="painel-hero-stat"><strong>' +
        (kpis.tarefas_pendentes || 0) +
        "</strong> " +
        __("tarefa(s) aberta(s)") +
        "</span>" +
        '<span class="painel-hero-stat"><strong>' +
        (resumo.parcelas_vencidas || 0) +
        "</strong> " +
        __("parcela(s) vencida(s)") +
        "</span>" +
        '<span class="painel-hero-stat painel-hero-stat--money"><strong class="painel-hero-money">' +
        fmt_currency(previsto_val, true) +
        "</strong> " +
        painel_periodo_previsto_label(periodo_dias) +
        "</span>";
    pulse_stats += "</div>";
    var pulse =
        pulse_stats +
        '<span class="painel-urgency-badge ' +
        urg +
        '">' +
        (urg === "alta" ? __("Atenção hoje") : __("Operação estável")) +
        "</span>";
    return (
        '<header class="painel-hero">' +
        '<h1 class="painel-hero-greeting">' +
        painel_greeting() +
        "</h1>" +
        '<p class="painel-hero-date">' +
        frappe.utils.escape_html(resumo.data_hoje || "") +
        "</p>" +
        '<p class="painel-hero-context">' +
        painel_context_html(resumo, kpis, periodo_dias, financeiro) +
        "</p>" +
        '<div class="painel-hero-pulse">' +
        pulse +
        "</div></header>"
    );
}

function render_acoes_rapidas() {
    var actions = [
        { label: __("Cliente"), icon: "user-plus", dt: "Cliente" },
        { label: __("Serviço"), icon: "folder-plus", dt: "Servico" },
        { label: __("Audiência"), icon: "calendar-plus-2", dt: "Audiencia" },
        { label: __("Prazo"), icon: "clock-plus", dt: "Controle de Prazos" },
        { label: __("Comunicação"), icon: "message-square-plus", dt: "Comunicacao" },
        { label: __("Tarefa"), icon: "list-plus", dt: "Tarefa" },
        { label: __("Honorário"), icon: "file-plus", dt: "Acordo de Honorarios Processuais" },
        { label: __("Pagamento"), icon: "circle-dollar-sign", dt: "Pagamento" },
        { label: __("Custa"), icon: "receipt", dt: "Custa Processual" },
        { label: __("Horas"), icon: "clock", dt: "Registro de Horas" },
        { label: __("Despesa"), icon: "wallet", dt: "Despesa do Escritorio" },
    ];
    var h =
        '<div class="painel-actions-wrap">' +
        '<p class="painel-actions-label">' +
        __("Ações rápidas") +
        "</p>" +
        '<div class="painel-actions">';
    actions.forEach(function (a) {
        h +=
            '<button type="button" class="painel-action-chip" data-new-dt="' +
            a.dt +
            '">' +
            painel_icon(a.icon) +
            "<span>" +
            a.label +
            "</span></button>";
    });
    h += "</div></div>";
    return h;
}

function render_filtros_painel(periodo_atual) {
    var opcoes_periodo = [
        { dias: 1, label: __("Hoje") },
        { dias: 7, label: __("7 dias") },
        { dias: 15, label: __("15 dias") },
        { dias: 30, label: __("30 dias") },
    ];
    var h =
        '<div class="painel-periodo-bar">' +
        '<div class="painel-filtro-group">' +
        '<span class="painel-periodo-label">' +
        painel_periodo_scope_label(periodo_atual) +
        "</span>" +
        '<div class="painel-periodo-filters">';
    opcoes_periodo.forEach(function (op) {
        h +=
            '<button type="button" class="painel-periodo-btn' +
            (periodo_atual === op.dias ? " active" : "") +
            '" data-periodo="' +
            op.dias +
            '">' +
            op.label +
            "</button>";
    });
    h += "</div></div></div>";
    return h;
}

function render_centro_atencao(centro, kpis, fin, horas, total_despesas, periodo_dias) {
    centro = centro || {};
    kpis = kpis || {};
    fin = fin || {};
    periodo_dias = cint(periodo_dias) || 7;

    function card(it) {
        return (
            '<div class="painel-atencao-card tone-' +
            it.tone +
            '" data-atencao-route="' +
            it.route +
            '">' +
            '<div class="painel-atencao-icon">' +
            painel_icon(it.icon) +
            "</div>" +
            '<div class="painel-atencao-body">' +
            '<div class="painel-atencao-count">' +
            frappe.utils.escape_html(String(it.count)) +
            "</div>" +
            '<div class="painel-atencao-label">' +
            frappe.utils.escape_html(it.label) +
            "</div>" +
            (it.meta
                ? '<div class="painel-atencao-meta">' +
                  frappe.utils.escape_html(String(it.meta)) +
                  "</div>"
                : "") +
            "</div></div>"
        );
    }

    function group(title, items) {
        var cards = items.map(card).join("");
        if (!cards) return "";
        return (
            '<div class="painel-centro-group">' +
            '<h3 class="painel-centro-group-title">' +
            frappe.utils.escape_html(title) +
            "</h3>" +
            '<div class="painel-centro-grid">' +
            cards +
            "</div></div>"
        );
    }

    var urgentes = [
        {
            tone: "red",
            icon: "calendar-days",
            count: centro.audiencias_hoje || 0,
            label: __("Audiências hoje"),
            route: "audiencias_hoje",
        },
        {
            tone: "orange",
            icon: "calendar-clock",
            count: centro.audiencias_amanha || 0,
            label: __("Amanhã"),
            route: "audiencias_amanha",
        },
        {
            tone: "red",
            icon: "alarm-clock",
            count: centro.prazos_vencidos || 0,
            label: __("Prazos vencidos"),
            route: "prazos_vencidos",
        },
        {
            tone: "orange",
            icon: "timer",
            count: centro.prazos_proximos_3d || 0,
            label: __("Prazos 3 dias"),
            route: "prazos_proximos",
        },
        {
            tone: "yellow",
            icon: "list-todo",
            count: centro.tarefas_atrasadas || 0,
            label: __("Tarefas atrasadas"),
            route: "tarefas_atrasadas",
        },
        {
            tone: "red",
            icon: "circle-dollar-sign",
            count: (centro.parcelas_vencidas && centro.parcelas_vencidas.count) || 0,
            label: __("Parcelas vencidas"),
            meta: fmt_currency((centro.parcelas_vencidas && centro.parcelas_vencidas.valor) || 0, true),
            route: "parcelas_vencidas",
        },
    ];

    var no_periodo = [
        {
            tone: "orange",
            icon: "wallet",
            count: (centro.pagamentos_periodo && centro.pagamentos_periodo.count) || 0,
            label: painel_periodo_a_receber_label(periodo_dias),
            meta: fmt_currency((centro.pagamentos_periodo && centro.pagamentos_periodo.valor) || 0, true),
            route: "pagamentos_periodo",
        },
        {
            tone: "green",
            icon: "trending-up",
            count: (centro.recebimentos_periodo && centro.recebimentos_periodo.count) || 0,
            label: painel_periodo_recebidos_label(periodo_dias),
            meta: fmt_currency((centro.recebimentos_periodo && centro.recebimentos_periodo.valor) || 0, true),
            route: "recebimentos_periodo",
        },
    ];

    return (
        '<section class="painel-section painel-centro-atencao painel-priority-max" id="painel-centro-atencao">' +
        '<div class="painel-centro-shell">' +
        '<div class="painel-section-head painel-centro-head"><div><h2 class="painel-section-title">' +
        __("Centro de Atenção") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("O que exige sua atenção agora — {0}", [painel_periodo_enunciado(periodo_dias)]) +
        "</p></div></div>" +
        '<div class="painel-centro-groups">' +
        group(__("Urgente"), urgentes) +
        group(__("No período ({0})", [painel_periodo_label(periodo_dias)]), no_periodo) +
        "</div></div></section>"
    );
}

function painel_build_indicadores_items(centro, kpis, fin, horas, total_despesas, periodo_dias) {
    centro = centro || {};
    kpis = kpis || {};
    fin = fin || {};
    periodo_dias = cint(periodo_dias) || 7;
    return [
        {
            tone: "blue",
            icon: "calendar",
            count: centro.audiencias_periodo || kpis.audiencias_semana || 0,
            label: __("Audiências ({0})", [painel_periodo_label(periodo_dias)]),
            route: "audiencias_periodo",
        },
        {
            tone: "orange",
            icon: "time",
            count: centro.prazos_urgentes || kpis.prazos_urgentes || 0,
            label: __("Prazos críticos"),
            route: "prazos_criticos",
        },
        {
            tone: "yellow",
            icon: "checklist",
            count: centro.tarefas_pendentes || kpis.tarefas_pendentes || 0,
            label: __("Tarefas abertas"),
            route: "tarefas_pendentes",
        },
        {
            tone: "green",
            icon: "banknote",
            count: fmt_currency((kpis.recebido_mes && kpis.recebido_mes.valor) || 0, true),
            label: __("Receita mês"),
            route: "receita_mes",
        },
        {
            tone: "blue",
            icon: "file-text",
            count: centro.honorarios_ativos || kpis.honorarios_ativos || 0,
            label: __("Honorários ativos"),
            route: "honorarios_ativos",
        },
        {
            tone: "blue",
            icon: "clock",
            count: (horas || 0).toFixed(1) + " h",
            label: painel_horas_label(periodo_dias),
            route: "horas",
        },
        {
            tone: "gray",
            icon: "users",
            count: centro.total_clientes || kpis.total_clientes || 0,
            label: __("Clientes"),
            route: "clientes",
        },
        {
            tone: "green",
            icon: "percent",
            count: (fin.taxa_recebimento || kpis.taxa_recebimento || 0) + "%",
            label: __("Taxa receb."),
            route: "taxa_recebimento",
        },
        {
            tone: "blue",
            icon: "briefcase",
            count: centro.servicos_ativos || kpis.servicos_ativos || 0,
            label: __("Processos"),
            route: "processos_ativos",
        },
        {
            tone: "orange",
            icon: "receipt",
            count: centro.custas_abertas || kpis.custas_abertas || 0,
            label: __("Custas abertas"),
            route: "custas_abertas",
        },
        {
            tone: "orange",
            icon: "wallet",
            count: fmt_currency(total_despesas || 0, true),
            label: __("Despesas mês"),
            route: "despesas_mes",
        },
    ];
}

function render_indicadores_painel(centro, kpis, fin, horas, total_despesas, periodo_dias) {
    var items = painel_build_indicadores_items(
        centro,
        kpis,
        fin,
        horas,
        total_despesas,
        periodo_dias
    );

    function card(it) {
        return (
            '<div class="painel-atencao-card tone-' +
            it.tone +
            '" data-atencao-route="' +
            it.route +
            '">' +
            '<div class="painel-atencao-icon">' +
            painel_icon(it.icon) +
            "</div>" +
            '<div class="painel-atencao-body">' +
            '<div class="painel-atencao-count">' +
            frappe.utils.escape_html(String(it.count)) +
            "</div>" +
            '<div class="painel-atencao-label">' +
            frappe.utils.escape_html(it.label) +
            "</div></div></div>"
        );
    }

    return (
        '<section class="painel-section painel-priority-medium" id="painel-indicadores">' +
        '<div class="painel-section-head"><div><h2 class="painel-section-title">' +
        __("Indicadores") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Visão consolidada {0}", [painel_periodo_enunciado(periodo_dias)]) +
        "</p></div></div>" +
        '<div class="painel-centro-grid">' +
        items.map(card).join("") +
        "</div></section>"
    );
}

function painel_day_diff(date_str) {
    if (!date_str) return null;
    return frappe.datetime.get_day_diff(date_str, frappe.datetime.get_today());
}

function painel_timeline_when_label(data, hora, dias_restantes) {
    if (dias_restantes == null && data) {
        dias_restantes = painel_day_diff(data);
    }
    if (dias_restantes === 0) {
        return hora ? __("Hoje {0}", [hora]) : __("Hoje");
    }
    if (dias_restantes === 1) {
        return hora ? __("Amanhã {0}", [hora]) : __("Amanhã");
    }
    var base = fmt_date_iso(data);
    return hora ? base + " · " + hora : base;
}

function painel_find_proximas_audiencias(audiencias, timeline, limit) {
    limit = cint(limit) || 2;
    if (audiencias && audiencias.length) {
        return audiencias.slice(0, limit);
    }
    var found = [];
    if (timeline && timeline.length) {
        for (var i = 0; i < timeline.length && found.length < limit; i++) {
            if (timeline[i].tipo !== "audiencia") continue;
            found.push({
                name: timeline[i].docname,
                tipo: timeline[i].titulo,
                cliente: timeline[i].subtitulo,
                servico: timeline[i].detalhe,
                data: timeline[i].data,
                hora: timeline[i].hora,
                dias_restantes: painel_day_diff(timeline[i].data),
                vara_label: timeline[i].detalhe,
                modalidade: "Presencial",
                link_virtual: "",
            });
        }
    }
    return found;
}

function painel_audiencia_modalidade_html(a) {
    var mod = a.modalidade || "Presencial";
    var icon = mod === "Virtual" ? "video" : mod === "Híbrida" ? "monitor" : "map-pin";
    var cls =
        mod === "Virtual" ? "virtual" : mod === "Híbrida" ? "hibrida" : "presencial";
    return (
        '<span class="painel-prox-mod painel-prox-mod--' +
        cls +
        '">' +
        painel_icon(icon) +
        frappe.utils.escape_html(mod) +
        "</span>"
    );
}

function painel_audiencia_entrar_html(a) {
    var mod = a.modalidade || "Presencial";
    if (mod !== "Virtual" && mod !== "Híbrida") {
        return "";
    }
    if (a.link_virtual) {
        return (
            '<a class="painel-btn-entrar" href="' +
            frappe.utils.escape_html(a.link_virtual) +
            '" target="_blank" rel="noopener" onclick="event.stopPropagation();">' +
            painel_icon("external-link") +
            "<span>" +
            __("Entrar na audiência") +
            "</span></a>"
        );
    }
    return (
        '<span class="painel-btn-entrar painel-btn-entrar--muted" title="' +
        frappe.utils.escape_html(__("Link ainda não cadastrado")) +
        '">' +
        __("Sem link") +
        "</span>"
    );
}

function render_proxima_audiencia_card(a, ordem) {
    var when = painel_timeline_when_label(a.data, a.hora, a.dias_restantes);
    var mod = a.modalidade || "Presencial";
    var local =
        a.vara_label ||
        (mod === "Presencial" || mod === "Híbrida" ? a.local_vara || "" : "");
    var entrar = painel_audiencia_entrar_html(a);
    var h =
        '<div class="painel-prox-card" data-dt="Audiencia" data-dn="' +
        frappe.utils.escape_html(a.name || "") +
        '">' +
        '<div class="painel-prox-card-head">' +
        '<div class="painel-prox-when">' +
        (ordem
            ? '<span class="painel-prox-ordem">' +
              frappe.utils.escape_html(__("#{0}", [ordem])) +
              " · " +
              "</span>"
            : "") +
        frappe.utils.escape_html(when) +
        "</div>" +
        painel_audiencia_modalidade_html(a) +
        "</div>" +
        '<div class="painel-prox-tipo">' +
        frappe.utils.escape_html(a.tipo || __("Audiência")) +
        "</div>" +
        '<div class="painel-prox-meta">' +
        '<div class="painel-prox-row"><span class="painel-prox-row-label">' +
        __("Cliente") +
        '</span><span class="painel-prox-row-value">' +
        frappe.utils.escape_html(a.cliente_nome || a.cliente || "—") +
        "</span></div>" +
        '<div class="painel-prox-row"><span class="painel-prox-row-label">' +
        __("Serviço") +
        '</span><span class="painel-prox-row-value">' +
        frappe.utils.escape_html(a.servico || "—") +
        "</span></div>";
    if (local && mod !== "Virtual") {
        h +=
            '<div class="painel-prox-row"><span class="painel-prox-row-label">' +
            __("Local") +
            '</span><span class="painel-prox-row-value">' +
            frappe.utils.escape_html(local) +
            "</span></div>";
    }
    h += "</div>";
    if (entrar) {
        h += '<div class="painel-prox-actions">' + entrar + "</div>";
    }
    h += "</div>";
    return h;
}

function render_proxima_audiencia(audiencias, timeline) {
    var items = painel_find_proximas_audiencias(audiencias, timeline, 2);
    var h =
        '<div class="painel-prox-audiencia painel-priority-max" id="painel-prox-audiencia">' +
        '<div class="painel-prox-audiencia-head">' +
        '<span class="painel-prox-badge">' +
        painel_icon("calendar-days") +
        "</span>" +
        '<h3 class="painel-prox-title">' +
        __("Próximas Audiências") +
        "</h3></div>";

    if (!items.length) {
        return (
            h +
            '<div class="painel-prox-empty">' +
            __("Nenhuma audiência agendada.") +
            "</div></div>"
        );
    }

    h += '<div class="painel-prox-list">';
    items.forEach(function (a, idx) {
        h += render_proxima_audiencia_card(a, idx + 1);
    });
    h += "</div></div>";
    return h;
}

function painel_calc_saude_operacional(centro, kpis, fin) {
    centro = centro || {};
    kpis = kpis || {};
    fin = fin || {};
    var vencidos =
        (centro.prazos_vencidos || 0) +
        ((centro.parcelas_vencidas && centro.parcelas_vencidas.count) || 0) +
        (centro.tarefas_atrasadas || 0);
    var pendentes = centro.tarefas_pendentes || kpis.tarefas_pendentes || 0;
    var previstos =
        (centro.pagamentos_periodo && centro.pagamentos_periodo.count) ||
        (fin.previsto_periodo && fin.previsto_periodo.count) ||
        0;
    var honorarios = centro.honorarios_ativos || kpis.honorarios_ativos || 0;
    var atencao =
        (centro.prazos_proximos_3d || 0) + (centro.prazos_urgentes || kpis.prazos_urgentes || 0);
    var penal = Math.min(
        85,
        vencidos * 4 + atencao * 1.5 + (centro.tarefas_atrasadas || 0) * 2
    );
    var score = Math.round(Math.max(0, Math.min(100, 100 - penal)));
    var label =
        score >= 85
            ? __("Excelente")
            : score >= 70
              ? __("Boa")
              : score >= 50
                ? __("Atenção")
                : __("Crítica");
    var tone = score >= 85 ? "green" : score >= 70 ? "blue" : score >= 50 ? "orange" : "red";
    return {
        score: score,
        label: label,
        tone: tone,
        vencidos: vencidos,
        pendentes: pendentes,
        previstos: previstos,
        honorarios: honorarios,
    };
}

function render_saude_operacional(centro, kpis, fin) {
    var s = painel_calc_saude_operacional(centro, kpis, fin);
    var circumference = 2 * Math.PI * 36;
    var offset = circumference - (circumference * s.score) / 100;
    return (
        '<div class="painel-saude-card painel-priority-max" id="painel-saude-operacional">' +
        '<div class="painel-saude-head">' +
        '<span class="painel-saude-badge tone-' +
        s.tone +
        '">' +
        painel_icon("activity") +
        "</span>" +
        '<h3 class="painel-saude-title">' +
        __("Saúde Operacional") +
        "</h3></div>" +
        '<div class="painel-saude-body">' +
        '<div class="painel-saude-score-wrap">' +
        '<div class="painel-saude-ring">' +
        '<svg viewBox="0 0 88 88" aria-hidden="true">' +
        '<circle class="painel-saude-ring-bg" cx="44" cy="44" r="36"></circle>' +
        '<circle class="painel-saude-ring-fill tone-' +
        s.tone +
        '" cx="44" cy="44" r="36" stroke-dasharray="' +
        circumference +
        '" stroke-dashoffset="' +
        offset +
        '"></circle></svg>' +
        '<div class="painel-saude-score-text">' +
        '<span class="painel-saude-score-num">' +
        s.score +
        "%</span>" +
        '<span class="painel-saude-score-label">' +
        frappe.utils.escape_html(s.label) +
        "</span></div></div>" +
        '<div class="painel-saude-summary">' +
        "<h4>" +
        frappe.utils.escape_html(s.label) +
        "</h4>" +
        "<p>" +
        __("Consolidado a partir dos indicadores operacionais já exibidos no painel.") +
        "</p></div></div>" +
        '<div class="painel-saude-rows">' +
        '<div class="painel-saude-row"><span class="painel-saude-dot red"></span><span><strong>' +
        s.vencidos +
        "</strong> " +
        __("itens vencidos ou críticos") +
        "</span></div>" +
        '<div class="painel-saude-row"><span class="painel-saude-dot orange"></span><span><strong>' +
        s.pendentes +
        "</strong> " +
        __("tarefas pendentes") +
        "</span></div>" +
        '<div class="painel-saude-row"><span class="painel-saude-dot green"></span><span><strong>' +
        s.previstos +
        "</strong> " +
        __("recebimentos previstos") +
        "</span></div>" +
        '<div class="painel-saude-row"><span class="painel-saude-dot green"></span><span><strong>' +
        s.honorarios +
        "</strong> " +
        __("honorários ativos") +
        "</span></div></div></div></div>"
    );
}

function painel_init_finance_chart($root, fin, page) {
    if (!fin || !fin.grafico || typeof frappe.Chart === "undefined") return;
    var $el = $root.find("#painel-finance-donut");
    if (!$el.length) return;
    if (page && page.painel_finance_chart) {
        try {
            page.painel_finance_chart.destroy();
        } catch (e) {
            /* ignore */
        }
        page.painel_finance_chart = null;
    }
    var labels = [];
    var values = [];
    var colors = [];
    var css = getComputedStyle(document.documentElement);
    var tone_colors = {
        danger: css.getPropertyValue("--red-500").trim(),
        success: css.getPropertyValue("--green-500").trim(),
        warning: css.getPropertyValue("--orange-500").trim(),
        neutral: css.getPropertyValue("--gray-600").trim(),
    };
    (fin.grafico || []).forEach(function (g) {
        if (flt(g.valor) <= 0) return;
        labels.push(g.label);
        values.push(flt(g.valor));
        colors.push(tone_colors[g.tone] || tone_colors.neutral);
    });
    if (!values.length) return;
    page.painel_finance_chart = new frappe.Chart($el[0], {
        type: "donut",
        height: 220,
        data: {
            labels: labels,
            datasets: [{ values: values }],
        },
        colors: colors,
        tooltipOptions: {
            formatTooltipY: function (d) {
                return format_currency(d, "BRL");
            },
        },
    });
}

function render_timeline(timeline, periodo_dias, list_meta, list_limit) {
    periodo_dias = cint(periodo_dias) || 7;
    var titulo =
        periodo_dias === 1
            ? __("Agenda de hoje")
            : __("Agenda — próximos {0} dias", [periodo_dias]);
    var subtitulo =
        periodo_dias === 1
            ? __("Audiências, prazos e tarefas de hoje")
            : __("Audiências, prazos e tarefas {0}", [painel_periodo_enunciado(periodo_dias)]);
    var meta_html = painel_list_meta_html(list_meta, list_limit);
    var h =
        '<section class="painel-section painel-section--timeline painel-priority-high" id="painel-timeline"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        titulo +
        "</h2>" +
        '<p class="painel-section-sub">' +
        subtitulo +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
        render_list_limit_controls("timeline", list_limit) +
        meta_html +
        '<span class="painel-section-link" data-route-calendar="1">' +
        __("Ver agenda") +
        "</span></div></div>";

    if (!timeline || !timeline.length) {
        return (
            h +
            '<div class="painel-panel">' +
            render_empty_state(
                "calendar",
                __("Agenda tranquila"),
                periodo_dias === 1
                    ? __("Nada agendado para hoje.")
                    : __("Nenhum compromisso no período selecionado.")
            ) +
            "</div></section>"
        );
    }

    h += '<div class="painel-panel"><div class="painel-timeline-modern">';
    timeline.forEach(function (it) {
        var tipo_label =
            it.tipo === "audiencia"
                ? __("Audiência")
                : it.tipo === "prazo"
                  ? __("Prazo")
                  : __("Tarefa");
        var tipo_icon =
            it.tipo === "audiencia" ? "milestone" : it.tipo === "prazo" ? "time" : "checklist";
        var pill_map = {
            red: "Alta",
            orange: "Média",
            yellow: "Normal",
            blue: "Normal",
            gray: "Baixa",
        };
        var tone = it.urgencia || "blue";
        var dias =
            it.dias_restantes != null ? it.dias_restantes : painel_day_diff(it.data);
        var when = painel_timeline_when_label(it.data, it.hora, dias);
        h +=
            '<div class="painel-tl-item tone-' +
            tone +
            '" data-dt="' +
            frappe.utils.escape_html(it.doctype || "") +
            '" data-dn="' +
            frappe.utils.escape_html(it.docname || "") +
            '">' +
            '<span class="painel-tl-marker" aria-hidden="true"></span>' +
            '<div class="painel-tl-content">' +
            '<div class="painel-tl-when">' +
            frappe.utils.escape_html(when) +
            "</div>" +
            '<div class="painel-tl-type">' +
            painel_icon(tipo_icon) +
            frappe.utils.escape_html(tipo_label) +
            "</div>" +
            '<div class="painel-tl-title">' +
            frappe.utils.escape_html(it.titulo || "") +
            "</div>" +
            '<div class="painel-tl-sub">' +
            frappe.utils.escape_html(it.subtitulo || "") +
            (it.detalhe ? " · " + frappe.utils.escape_html(it.detalhe) : "") +
            "</div></div>" +
            status_pill(pill_map[tone] || "Normal") +
            "</div>";
    });
    h += "</div></div></section>";
    return h;
}

function render_kpis_operacionais(k, fin, horas, total_despesas, total_custas, custas_list) {
    if (!k) return "";
    fin = fin || {};
    var row1 = [
        { label: __("Audiências da semana"), value: String(k.audiencias_semana || 0), route: "audiencias_semana" },
        { label: __("Prazos críticos"), value: String(k.prazos_urgentes || 0), urgent: k.prazos_urgentes > 0, route: "prazos_criticos" },
        { label: __("Tarefas pendentes"), value: String(k.tarefas_pendentes || 0), route: "tarefas_pendentes" },
        {
            label: __("Recebimentos do período"),
            value: fmt_currency((k.recebido_periodo && k.recebido_periodo.valor) || 0),
            positive: true,
            route: "recebimentos_periodo",
        },
    ];
    var row2 = [
        { label: __("Receita do mês"), value: fmt_currency((k.recebido_mes && k.recebido_mes.valor) || 0), positive: true, route: "receita_mes" },
        { label: __("Honorários ativos"), value: String(k.honorarios_ativos || 0), route: "honorarios_ativos" },
        { label: __("Horas registradas"), value: (horas || 0).toFixed(1) + " h", route: "horas" },
        { label: __("Clientes ativos"), value: String(k.total_clientes || 0), route: "clientes" },
    ];
    var row3 = [
        { label: __("Taxa de recebimento"), value: (fin.taxa_recebimento || k.taxa_recebimento || 0) + "%", route: "taxa_recebimento" },
        { label: __("Processos ativos"), value: String(k.servicos_ativos || 0), route: "processos_ativos" },
        {
            label: __("Custas abertas"),
            value: String(k.custas_abertas || (custas_list && custas_list.length) || 0),
            warn: (k.custas_abertas || 0) > 0,
            route: "custas_abertas",
        },
        { label: __("Despesas do mês"), value: fmt_currency(total_despesas || 0), route: "despesas_mes" },
    ];

    var h =
        '<section class="painel-section" id="painel-kpis"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("KPIs Operacionais") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Indicadores do período selecionado") +
        "</p></div></div>";

    [row1, row2, row3].forEach(function (row) {
        h += '<div class="painel-kpi-row">';
        row.forEach(function (item) {
            var cls = "painel-kpi";
            if (item.urgent) cls += " urgent";
            if (item.positive) cls += " positive";
            if (item.warn) cls += " warn";
            h +=
                '<div class="' +
                cls +
                '" data-kpi-route="' +
                (item.route || "") +
                '">' +
                '<div class="painel-kpi-label">' +
                item.label +
                "</div>" +
                '<div class="painel-kpi-value">' +
                item.value +
                "</div></div>";
        });
        h += "</div>";
    });
    h += "</section>";
    return h;
}

function render_comunicacoes_pendentes(comunicacoes, periodo_dias, list_meta, list_limit) {
    periodo_dias = cint(periodo_dias) || 7;
    var meta_html = painel_list_meta_html(list_meta, list_limit);
    var h =
        '<section class="painel-section painel-priority-high" id="painel-comunicacoes"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Comunicações") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Follow-ups pendentes — visão {0}", [painel_periodo_enunciado(periodo_dias)]) +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
        render_list_limit_controls("comunicacoes", list_limit) +
        meta_html +
        '<span class="painel-section-link" data-route-list="Comunicacao">' +
        __("Ver todas") +
        "</span></div></div>";

    if (!comunicacoes || !comunicacoes.length) {
        return (
            h +
            '<div class="painel-panel">' +
            render_success_state(
                __("Nenhuma comunicação pendente"),
                __("Retornos e follow-ups aparecerão aqui quando precisarem de ação.")
            ) +
            "</div></section>"
        );
    }

    h += '<div class="painel-panel"><div class="painel-schedule-list">';
    comunicacoes.forEach(function (c) {
        var urg = c.urgencia_ordem === 0 ? "red" : c.urgencia_ordem === 1 ? "orange" : "yellow";
        var status_label = urg === "red" ? __("Alta") : urg === "orange" ? __("Média") : __("Normal");
        h +=
            '<div class="painel-com-item" data-comunicacao="' +
            frappe.utils.escape_html(c.name || "") +
            '" data-dt="Comunicacao" data-dn="' +
            frappe.utils.escape_html(c.name || "") +
            '">' +
            '<div class="painel-com-main">' +
            '<div class="painel-com-cliente">' +
            frappe.utils.escape_html(c.cliente_nome || c.cliente || __("Sem cliente")) +
            "</div>" +
            '<div class="painel-com-assunto">' +
            frappe.utils.escape_html(c.assunto || c.name) +
            "</div>" +
            (c.motivo_pendencia
                ? '<div class="painel-com-meta">' +
                  frappe.utils.escape_html(c.motivo_pendencia) +
                  "</div>"
                : "") +
            "</div>" +
            '<div class="painel-com-side">' +
            status_pill(status_label) +
            '<span class="painel-com-dias">' +
            __("{0}d sem retorno", [c.dias_sem_retorno || 0]) +
            "</span></div></div>";
    });
    h += "</div></div></section>";
    return h;
}

function bind_painel_filters($root, page) {
    $root.find(".painel-periodo-btn").on("click", function () {
        var dias = cint($(this).attr("data-periodo"));
        if (!page || dias === page.painel_periodo) return;
        page.painel_periodo = dias;
        load_painel(page);
    });
    $root.find(".painel-linhas-btn").on("click", function () {
        var list_key = $(this).attr("data-list");
        var linhas = cint($(this).attr("data-linhas"));
        if (!page || !list_key) return;
        if (!page.painel_list_limits) {
            page.painel_list_limits = painel_default_list_limits();
        }
        if (linhas === page.painel_list_limits[list_key]) return;
        page.painel_list_limits[list_key] = linhas;
        load_painel(page);
    });
}

function bind_atencao_routes($root, page) {
    var hoje = frappe.datetime.get_today();
    var amanha = frappe.datetime.add_days(hoje, 1);
    var tres_dias = frappe.datetime.add_days(hoje, 3);
    var periodo_fim = painel_periodo_fim(page);
    var mes_inicio = frappe.datetime.month_start(hoje);
    var mes_fim = frappe.datetime.month_end(hoje);

    var routes = {
        audiencias_hoje: function () {
            painel_goto_list("Audiencia", [
                ["data_hora", "between", [hoje + " 00:00:00", hoje + " 23:59:59"]],
            ]);
        },
        audiencias_amanha: function () {
            painel_goto_list("Audiencia", [
                ["data_hora", "between", [amanha + " 00:00:00", amanha + " 23:59:59"]],
            ]);
        },
        audiencias_periodo: function () {
            painel_goto_list("Audiencia", [
                ["data_hora", "between", [hoje + " 00:00:00", periodo_fim + " 23:59:59"]],
            ]);
        },
        prazos_vencidos: function () {
            painel_goto_list("Controle de Prazos", [
                ["status", "=", "Pendente"],
                ["data_prazo", "<", hoje],
            ]);
        },
        prazos_proximos: function () {
            painel_goto_list("Controle de Prazos", [
                ["status", "=", "Pendente"],
                ["data_prazo", "between", [hoje, tres_dias]],
            ]);
        },
        prazos_criticos: function () {
            painel_goto_list("Controle de Prazos", [
                ["status", "=", "Pendente"],
                ["data_prazo", "<=", tres_dias],
            ]);
        },
        tarefas_atrasadas: function () {
            painel_goto_list("Tarefa", [
                ["status", "in", ["Pendente", "Em Andamento"]],
                ["data_limite", "<", hoje],
            ]);
        },
        tarefas_pendentes: function () {
            painel_goto_list("Tarefa", [["status", "in", ["Pendente", "Em Andamento"]]]);
        },
        parcelas_vencidas: function () {
            painel_goto_list("Pagamento", [["status", "=", "Vencido"]]);
        },
        pagamentos_periodo: function () {
            painel_goto_list("Pagamento", [
                ["status", "=", "Pendente"],
                ["data_vencimento", "between", [hoje, periodo_fim]],
            ]);
        },
        recebimentos_periodo: function () {
            painel_goto_list("Pagamento", [
                ["status", "in", ["Recebido", "Repassado"]],
                ["data_recebimento", "between", [hoje, periodo_fim]],
            ]);
        },
        receita_mes: function () {
            painel_goto_list("Pagamento", [
                ["status", "in", ["Recebido", "Repassado"]],
                ["data_recebimento", "between", [mes_inicio, mes_fim]],
            ]);
        },
        honorarios_ativos: function () {
            painel_goto_list("Acordo de Honorarios Processuais", [["status", "=", "Vigente"]]);
        },
        horas: function () {
            painel_goto_list("Registro de Horas", [
                ["data", "between", [hoje, periodo_fim]],
            ]);
        },
        clientes: function () {
            painel_goto_list("Cliente", []);
        },
        taxa_recebimento: function () {
            frappe.set_route("query-report", "inadimplencia");
        },
        processos_ativos: function () {
            painel_goto_list("Servico", [["status", "=", "Em andamento"]]);
        },
        custas_abertas: function () {
            painel_goto_list("Custa Processual", [
                ["status", "in", ["Pendente", "Pago"]],
                ["repassar_cliente", "=", 1],
            ]);
        },
        despesas_mes: function () {
            painel_goto_list("Despesa do Escritorio", [
                ["data_vencimento", "between", [mes_inicio, mes_fim]],
            ]);
        },
    };

    $root.find(".painel-atencao-card[data-atencao-route]").on("click", function () {
        var key = $(this).attr("data-atencao-route");
        if (routes[key]) routes[key]();
    });
}

function cint(val) {
    return parseInt(val, 10) || 0;
}

function render_kpis(k) {
    if (!k) return "";
    var items = [
        {
            key: "vencidas",
            label: __("Parcelas vencidas"),
            value: fmt_currency(k.parcelas_vencidas.valor),
            meta: __("{0} parcela(s)", [k.parcelas_vencidas.count]),
            urgent: true,
        },
        {
            key: "recebido",
            label: __("Recebido este mês"),
            value: fmt_currency(k.recebido_mes.valor),
            meta: __("{0} recebida(s)", [k.recebido_mes.count]),
            positive: true,
        },
        {
            key: "previsto",
            label: __("Previsto no mês"),
            value: fmt_currency((k.previsto_mes && k.previsto_mes.valor) || 0),
            meta: __("{0} pendente(s)", [(k.previsto_mes && k.previsto_mes.count) || 0]),
            warn: true,
        },
        {
            key: "audiencias",
            label: __("Audiências hoje"),
            value: String(k.audiencias_hoje != null ? k.audiencias_hoje : 0),
            meta: __("{0} na semana", [k.audiencias_semana]),
        },
        {
            key: "prazos",
            label: __("Prazos urgentes"),
            value: String(k.prazos_urgentes),
            meta: __("até 3 dias"),
            urgent: k.prazos_urgentes > 0,
        },
        {
            key: "servicos",
            label: __("Serviços ativos"),
            value: String(k.servicos_ativos),
            meta: __("{0} clientes", [k.total_clientes]),
        },
    ];
    var h =
        '<section class="painel-section"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Indicadores") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Visão rápida do escritório") +
        "</p></div></div>" +
        '<div class="painel-kpi-grid">';
    items.forEach(function (item) {
        var cls = "painel-kpi";
        if (item.urgent) cls += " urgent";
        if (item.positive) cls += " positive";
        if (item.warn) cls += " warn";
        h +=
            '<div class="' +
            cls +
            '" data-kpi="' +
            item.key +
            '">' +
            '<div class="painel-kpi-label">' +
            item.label +
            "</div>" +
            '<div class="painel-kpi-value">' +
            item.value +
            "</div>" +
            '<div class="painel-kpi-meta">' +
            (item.meta || "") +
            "</div></div>";
    });
    h += "</div></section>";
    return h;
}

function render_operacao_dia(d) {
    var timeline = build_timeline_items(d);
    var criticas = build_parcelas_criticas(d.parcelas, 5);
    var h =
        '<section class="painel-section painel-section--primary"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Operação do dia") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Central de urgências, agenda e cobrança imediata") +
        "</p></div></div>" +
        '<div class="painel-operacao-grid">';
    h +=
        '<div class="painel-panel"><div class="painel-panel-head">' +
        __("Agenda e urgências") +
        "</div>" +
        '<div class="painel-op-list">' +
        (timeline ||
            render_empty_state(
                "calendar",
                __("Agenda tranquila hoje"),
                __("Sem prazos ou audiências críticos para as próximas horas.")
            )) +
        "</div></div>";
    h +=
        '<div class="painel-panel" id="painel-parcelas-criticas"><div class="painel-panel-head">' +
        __("Parcelas críticas") +
        "</div>" +
        '<div class="painel-op-list">' +
        (criticas ||
            render_empty_state(
                "money",
                __("Nenhuma parcela vencida"),
                __("Honorários em dia — excelente controle de recebíveis.")
            )) +
        "</div></div>";
    h += "</div></section>";
    return h;
}

function build_timeline_items(d) {
    var items = [];
    (d.alertas || []).forEach(function (a) {
        items.push({
            sort: a.tipo === "prazo" && a.dias <= 0 ? 0 : 1,
            time: a.hora || (a.tipo === "prazo" ? __("Prazo") : __("Hoje")),
            title: a.titulo,
            sub:
                ((a.cliente_nome || a.cliente) ? (a.cliente_nome || a.cliente) + " · " : "") +
                (a.tipo === "prazo"
                    ? a.dias === 0
                        ? __("Vence hoje")
                        : __("Amanhã")
                    : __("Audiência")),
            doctype: a.doctype,
            docname: a.docname,
            pill: a.nivel === "red" ? "red" : "orange",
        });
    });
    (d.audiencias || []).forEach(function (a) {
        if (a.dias_restantes !== 0) return;
        items.push({
            sort: 2,
            time: a.hora || __("—"),
            title: a.tipo || __("Audiência"),
            sub: ((a.cliente_nome || a.cliente) || "") + (a.vara_label ? " · " + a.vara_label : ""),
            doctype: "Audiencia",
            docname: a.name,
            pill: "blue",
        });
    });
    (d.prazos || []).forEach(function (p) {
        if (p.dias_restantes > 1) return;
        items.push({
            sort: p.dias_restantes <= 0 ? 0 : 1,
            time: fmt_date_iso(p.data_prazo),
            title: p.descricao || p.name,
            sub: p.cliente_nome || "",
            doctype: "Controle de Prazos",
            docname: p.name,
            pill: p.dias_restantes <= 0 ? "red" : "orange",
        });
    });
    items.sort(function (a, b) {
        return a.sort - b.sort;
    });
    if (!items.length) return "";
    return items
        .map(function (it) {
            var hot = it.sort <= 1 ? " painel-op-item--hot" : "";
            return (
                '<div class="painel-op-item' +
                hot +
                '" data-dt="' +
                it.doctype +
                '" data-dn="' +
                frappe.utils.escape_html(it.docname) +
                '">' +
                '<div class="painel-op-time">' +
                frappe.utils.escape_html(String(it.time)) +
                "</div>" +
                '<div class="painel-op-body"><div class="painel-op-title">' +
                frappe.utils.escape_html(it.title) +
                '</div><div class="painel-op-sub">' +
                frappe.utils.escape_html(it.sub) +
                "</div></div>" +
                '<div class="painel-op-side">' +
                status_pill(it.pill === "red" ? "Alta" : it.pill === "orange" ? "Média" : "Normal") +
                "</div></div>"
            );
        })
        .join("");
}

function build_parcelas_criticas(parcelas, limit) {
    if (!parcelas || !parcelas.length) return "";
    var sorted = parcelas.slice().sort(function (a, b) {
        if (_is_vencido(a.status) && !_is_vencido(b.status)) return -1;
        if (_is_vencido(b.status) && !_is_vencido(a.status)) return 1;
        return (a.dias_atraso || 0) > (b.dias_atraso || 0) ? -1 : 1;
    });
    return sorted
        .slice(0, limit)
        .map(function (p) {
            var btn = "";
            if (_pagamento_pode_receber(p.status)) {
                btn =
                    '<button type="button" class="painel-btn-recebida" data-pagamento="' +
                    frappe.utils.escape_html(p.name || "") +
                    '">✓ ' +
                    __("Recebido") +
                    "</button>";
            }
            return (
                '<div class="painel-op-item painel-parcela-critica" data-acordo="' +
                frappe.utils.escape_html(p.parent || "") +
                '">' +
                '<div class="painel-op-body"><div class="painel-op-title">' +
                frappe.utils.escape_html(p.cliente_nome || "—") +
                '</div><div class="painel-op-sub">' +
                fmt_currency(p.valor_total) +
                " · " +
                fmt_date_iso(p.vencimento) +
                "</div></div>" +
                '<div class="painel-op-side">' +
                status_pill(p.status) +
                btn +
                "</div></div>"
            );
        })
        .join("");
}

function render_duo_honorarios_despesas(
    parcelas,
    despesas,
    total_mes,
    meta_parcelas,
    meta_despesas,
    limit_parcelas,
    limit_despesas
) {
    return (
        '<div class="painel-duo-grid" id="painel-duo-financeiro">' +
        render_parcelas(parcelas, true, meta_parcelas, limit_parcelas) +
        render_despesas(despesas, total_mes, true, meta_despesas, limit_despesas) +
        "</div>"
    );
}

function render_duo_custas_horas(custas, total_mes, horas, meta_custas, periodo_dias, limit_custas) {
    return (
        '<div class="painel-duo-grid" id="painel-duo-secundario">' +
        render_custas(custas, total_mes, true, meta_custas, limit_custas) +
        render_horas_semana(horas, true, periodo_dias) +
        "</div>"
    );
}

function render_financeiro(fin, periodo_dias) {
    if (!fin) return "";
    periodo_dias = cint(periodo_dias) || 7;
    var previsto =
        fin.previsto_periodo || fin.previsto_semana || { count: 0, valor: 0 };
    var previsto_label =
        periodo_dias === 1
            ? __("Previsto hoje")
            : __("Previsto ({0})", [painel_periodo_label(periodo_dias)]);
    var max_val = 1;
    (fin.grafico || []).forEach(function (g) {
        if (flt(g.valor) > max_val) max_val = flt(g.valor);
    });
    var chart_rows = (fin.grafico || [])
        .map(function (g) {
            var pct = Math.max(4, Math.round((flt(g.valor) / max_val) * 100));
            return (
                '<div class="painel-chart-row">' +
                '<span class="painel-chart-label">' +
                frappe.utils.escape_html(g.label) +
                "</span>" +
                '<div class="painel-chart-track"><div class="painel-chart-fill ' +
                (g.tone || "neutral") +
                '" style="width:' +
                pct +
                '%"></div></div>' +
                '<span class="painel-chart-amt">' +
                fmt_currency(g.valor) +
                "</span></div>"
            );
        })
        .join("");
    var taxa = fin.taxa_recebimento || 0;
    return (
        '<section class="painel-section painel-priority-low" id="painel-financeiro"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Financeiro") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Recebíveis e projeção {0}", [painel_periodo_enunciado(periodo_dias)]) +
        "</p></div></div>" +
        '<div class="painel-finance-grid">' +
        '<div class="painel-panel"><div class="painel-finance-stats">' +
        '<div class="painel-stat"><div class="painel-stat-label">' +
        __("Recebido no mês") +
        '</div><div class="painel-stat-value success">' +
        fmt_currency(fin.recebido_mes.valor) +
        "</div></div>" +
        '<div class="painel-stat"><div class="painel-stat-label">' +
        __("Vencido") +
        '</div><div class="painel-stat-value danger">' +
        fmt_currency(fin.vencido.valor) +
        "</div></div>" +
        '<div class="painel-stat"><div class="painel-stat-label">' +
        previsto_label +
        '</div><div class="painel-stat-value">' +
        fmt_currency(previsto.valor) +
        "</div></div>" +
        '<div class="painel-stat"><div class="painel-stat-label">' +
        __("Inadimplência") +
        '</div><div class="painel-stat-value danger">' +
        (fin.taxa_inadimplencia || 0) +
        "%</div></div>" +
        "</div></div>" +
        '<div class="painel-panel"><div class="painel-panel-head">' +
        __("Distribuição") +
        '</div><div id="painel-finance-donut" class="painel-finance-donut-wrap"></div>' +
        '<div class="painel-panel-head painel-panel-head--sub">' +
        __("Taxa de recebimento") +
        '</div><div class="painel-chart painel-chart--percent">' +
        '<div class="painel-chart-row">' +
        '<span class="painel-chart-label">' +
        __("Recebido") +
        "</span>" +
        '<div class="painel-chart-track"><div class="painel-chart-fill success" style="width:' +
        Math.max(4, Math.min(100, taxa)) +
        '%"></div></div>' +
        '<span class="painel-chart-amt">' +
        taxa +
        "%</span></div>" +
        chart_rows +
        "</div></div></div></section>"
    );
}

function render_parcelas(parcelas, compact, list_meta, list_limit) {
    var meta_html = painel_list_meta_html(list_meta, list_limit);
    var h =
        '<section class="painel-section' +
        (compact ? " painel-section--nested painel-priority-low" : " painel-priority-low") +
        '" id="painel-parcelas"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Honorários em aberto") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Pendentes e vencidos") +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
        render_list_limit_controls("parcelas", list_limit) +
        meta_html +
        '<span class="painel-section-link" data-route-list="Pagamento">' +
        __("Ver todos") +
        "</span></div></div>";
    if (!parcelas || !parcelas.length) {
        return (
            h +
            '<div class="painel-panel">' +
            render_empty_state(
                "tick",
                __("Honorários em dia"),
                __("Não há parcelas pendentes ou vencidas no momento.")
            ) +
            "</div></section>"
        );
    }
    h += '<div class="painel-panel">';
    parcelas.forEach(function (p) {
        var prazo_txt = "";
        if (_is_vencido(p.status) && p.dias_atraso > 0) {
            prazo_txt = __("Atraso {0}d", [p.dias_atraso]);
        } else if (p.status === "Pendente") {
            prazo_txt = p.dias_para_vencer === 0 ? __("Hoje") : __("Em {0}d", [p.dias_para_vencer]);
        }
        var btn = "";
        if (_pagamento_pode_receber(p.status)) {
            btn =
                '<button type="button" class="painel-btn-recebida" data-pagamento="' +
                frappe.utils.escape_html(p.name || "") +
                '">✓ ' +
                __("Recebido") +
                "</button>";
        }
        h +=
            '<div class="painel-list-item painel-parcela-card painel-row-acordo" data-acordo="' +
            frappe.utils.escape_html(p.parent || "") +
            '">' +
            '<div class="painel-parcela-main"><div class="painel-op-title">' +
            frappe.utils.escape_html(p.cliente_nome || "—") +
            '</div><div class="painel-op-sub">' +
            frappe.utils.escape_html(p.servico_titulo || p.servico_tipo || "") +
            (p.numero_processo ? " · " + frappe.utils.escape_html(p.numero_processo) : "") +
            "</div>" +
            '<div class="painel-muted">' +
            fmt_date_iso(p.vencimento) +
            (prazo_txt ? " · " + prazo_txt : "") +
            "</div>" +
            status_pill(p.status) +
            "</div>" +
            '<div class="painel-list-side">' +
            '<div class="painel-list-valor ' +
            (_is_vencido(p.status) ? "danger" : "warn") +
            '">' +
            fmt_currency(p.valor_total) +
            "</div>" +
            btn +
            "</div></div>";
    });
    h += "</div></section>";
    return h;
}

function render_despesas(despesas, total_mes, compact, list_meta, list_limit) {
    var meta_html = painel_list_meta_html(list_meta, list_limit);
    var h =
        '<section class="painel-section' +
        (compact ? " painel-section--nested painel-priority-low" : " painel-priority-low") +
        '" id="painel-despesas"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Despesas") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Pendentes · mês calendário: {0}", [fmt_currency(total_mes || 0, true)]) +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
        render_list_limit_controls("despesas", list_limit) +
        meta_html +
        '<span class="painel-section-link" data-route-list="Despesa do Escritorio">' +
        __("Ver todas") +
        "</span></div></div>";

    if (!despesas || !despesas.length) {
        return (
            h +
            '<div class="painel-panel">' +
            render_empty_state(
                "wallet",
                __("Nenhuma despesa pendente"),
                __("Despesas operacionais aparecerão aqui quando cadastradas.")
            ) +
            "</div></section>"
        );
    }

    h += '<div class="painel-panel"><div class="painel-schedule-list">';
    despesas.forEach(function (d) {
        var tone = d.status === "Atrasado" ? "danger" : "warn";
        var badge =
            d.status === "Atrasado"
                ? '<span class="indicator-pill red">' + __("Atrasado") + "</span>"
                : '<span class="indicator-pill orange">' + __("Pendente") + "</span>";
        h +=
            '<div class="painel-list-item painel-schedule-item painel-row-despesa" data-despesa="' +
            frappe.utils.escape_html(d.name || "") +
            '">' +
            '<div class="painel-schedule-main">' +
            '<div class="painel-op-title">' +
            frappe.utils.escape_html(d.descricao || d.name) +
            "</div>" +
            '<div class="painel-op-sub">' +
            frappe.utils.escape_html(d.categoria || "") +
            (d.data_vencimento
                ? " · " + frappe.utils.escape_html(frappe.datetime.str_to_user(d.data_vencimento))
                : "") +
            "</div>" +
            badge +
            "</div>" +
            '<div class="painel-list-side">' +
            '<div class="painel-list-valor ' +
            tone +
            '">' +
            fmt_currency(d.valor) +
            "</div></div></div>";
    });
    h += "</div></div></section>";
    return h;
}

function render_custas(custas, total_mes, compact, list_meta, list_limit) {
    var meta_html = painel_list_meta_html(list_meta, list_limit);
    var h =
        '<section class="painel-section' +
        (compact ? " painel-section--nested painel-priority-low" : " painel-priority-low") +
        '" id="painel-custas"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Custas") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Repasse · mês calendário: {0}", [fmt_currency(total_mes || 0, true)]) +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
        render_list_limit_controls("custas", list_limit) +
        meta_html +
        '<span class="painel-section-link" data-route-list="Custa Processual">' +
        __("Ver todas") +
        "</span></div></div>";

    if (!custas || !custas.length) {
        return (
            h +
            '<div class="painel-panel">' +
            render_empty_state(
                "receipt",
                __("Nenhuma custa pendente de repasse"),
                __("Custas pagas marcadas para repasse aparecerão aqui.")
            ) +
            "</div></section>"
        );
    }

    h += '<div class="painel-panel"><div class="painel-schedule-list">';
    custas.forEach(function (c) {
        h +=
            '<div class="painel-list-item painel-schedule-item" data-custa="' +
            frappe.utils.escape_html(c.name || "") +
            '">' +
            '<div class="painel-schedule-main">' +
            '<div class="painel-op-title">' +
            frappe.utils.escape_html(c.descricao || c.name) +
            "</div>" +
            '<div class="painel-op-sub">' +
            frappe.utils.escape_html(c.tipo || "") +
            (c.servico_titulo ? " · " + frappe.utils.escape_html(c.servico_titulo) : "") +
            "</div>" +
            '<span class="indicator-pill blue">' + __("Aguardando repasse") + "</span>" +
            "</div>" +
            '<div class="painel-list-side">' +
            '<div class="painel-list-valor warn">' +
            fmt_currency(c.valor) +
            "</div></div></div>";
    });
    h += "</div></div></section>";
    return h;
}

function render_horas_semana(horas, compact, periodo_dias) {
    periodo_dias = cint(periodo_dias) || 7;
    return (
        '<section class="painel-section' +
        (compact ? " painel-section--nested painel-priority-low" : " painel-section--inline painel-priority-low") +
        '" id="painel-horas">' +
        '<div class="painel-section-head"><div><h2 class="painel-section-title">' +
        __("Horas") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Registradas {0}", [painel_periodo_enunciado(periodo_dias)]) +
        "</p></div>" +
        '<span class="painel-section-link" data-route-list="Registro de Horas">' +
        __("Ver todas") +
        "</span></div>" +
        '<div class="painel-panel painel-horas-panel">' +
        '<div class="painel-atencao-count">' +
        (horas || 0).toFixed(1) +
        " h</div></div></section>"
    );
}

function render_comunicacoes(comunicacoes) {
    var h =
        '<section class="painel-section" id="painel-comunicacoes"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Últimas Comunicações") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Interações recentes com clientes") +
        "</p></div>" +
        '<span class="painel-section-link" data-route-list="Comunicacao">' +
        __("Ver todas") +
        "</span></div>";

    if (!comunicacoes || !comunicacoes.length) {
        return (
            h +
            '<div class="painel-panel">' +
            render_empty_state(
                "message",
                __("Nenhuma comunicação registrada"),
                __("Ligações, e-mails e reuniões aparecerão aqui.")
            ) +
            "</div></section>"
        );
    }

    h += '<div class="painel-panel"><div class="painel-schedule-list">';
    comunicacoes.forEach(function (c) {
        h +=
            '<div class="painel-schedule-item" data-comunicacao="' +
            frappe.utils.escape_html(c.name || "") +
            '">' +
            '<div class="painel-schedule-main">' +
            '<div class="painel-op-title">' +
            frappe.utils.escape_html(c.assunto || c.name) +
            "</div>" +
            '<div class="painel-op-sub">' +
            frappe.utils.escape_html(c.tipo || "") +
            ((c.cliente_nome || c.cliente) ? " · " + frappe.utils.escape_html(c.cliente_nome || c.cliente) : "") +
            "</div></div>" +
            '<div class="painel-schedule-side">' +
            (c.data
                ? '<span class="painel-op-sub">' +
                  frappe.utils.escape_html(frappe.datetime.str_to_user(c.data)) +
                  "</span>"
                : "") +
            "</div></div>";
    });
    h += "</div></div></section>";
    return h;
}

function render_secundario(title, icon, body, section_id, emptyTitle, emptyHint, list_doctype) {
    var foot = "";
    if (list_doctype && body) {
        foot =
            '<div class="painel-section-foot">' +
            '<span class="painel-section-foot-link" data-route-list="' +
            frappe.utils.escape_html(list_doctype) +
            '">' +
            __("Ver todos") +
            "</span></div>";
    }
    return (
        '<section class="painel-section painel-section--secondary" id="' +
        section_id +
        '"><div class="painel-section-head">' +
        "<h2 class='painel-section-title'>" +
        title +
        "</h2></div>" +
        '<div class="painel-panel">' +
        (body
            ? '<div class="painel-schedule-list">' + body + "</div>" + foot
            : render_empty_state(icon, emptyTitle, emptyHint)) +
        "</div></section>"
    );
}

function painel_date_parts(iso) {
    if (!iso) {
        return { day: "—", month: "" };
    }
    var months = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
    var d = frappe.datetime.str_to_obj(iso);
    return {
        day: String(d.getDate()).padStart(2, "0"),
        month: months[d.getMonth()] || "",
    };
}

function prazo_countdown_label(dias) {
    if (dias < 0) {
        return { text: __("Vencido"), cls: "danger" };
    }
    if (dias === 0) {
        return { text: __("Hoje"), cls: "warn" };
    }
    if (dias === 1) {
        return { text: __("Amanhã"), cls: "warn" };
    }
    return { text: __("Em {0}d", [dias]), cls: "" };
}

function render_audiencia_items(audiencias) {
    if (!audiencias || !audiencias.length) return "";
    return audiencias
        .map(function (a) {
            var parts = painel_date_parts(a.data);
            var card_cls = "painel-schedule-card";
            if (a.dias_restantes === 0) card_cls += " painel-schedule-card--today";
            var btn = "";
            if (a.modalidade === "Virtual") {
                if (a.link_virtual) {
                    btn =
                        '<a class="painel-btn-entrar" href="' +
                        frappe.utils.escape_html(a.link_virtual) +
                        '" target="_blank" rel="noopener" onclick="event.stopPropagation();">' +
                        __("Entrar") +
                        "</a>";
                } else {
                    btn =
                        '<span class="painel-btn-entrar painel-btn-entrar--muted" title="' +
                        frappe.utils.escape_html(__("Link ainda não cadastrado")) +
                        '">' +
                        __("Sem link") +
                        "</span>";
                }
            }
            return (
                '<div class="' +
                card_cls +
                '" data-dt="Audiencia" data-dn="' +
                frappe.utils.escape_html(a.name) +
                '">' +
                '<div class="painel-schedule-when">' +
                '<span class="painel-schedule-day">' +
                frappe.utils.escape_html(parts.day) +
                "</span>" +
                '<span class="painel-schedule-month">' +
                frappe.utils.escape_html(parts.month) +
                "</span>" +
                (a.hora
                    ? '<span class="painel-schedule-hour">' + frappe.utils.escape_html(a.hora) + "</span>"
                    : "") +
                "</div>" +
                '<div class="painel-schedule-body">' +
                '<div class="painel-schedule-title">' +
                frappe.utils.escape_html(a.cliente_nome || a.cliente || "—") +
                "</div>" +
                '<div class="painel-schedule-sub">' +
                frappe.utils.escape_html(a.tipo || __("Audiência")) +
                (a.vara_label ? " · " + frappe.utils.escape_html(a.vara_label) : "") +
                "</div></div>" +
                '<div class="painel-schedule-meta">' +
                status_pill(a.modalidade || "Presencial") +
                btn +
                "</div></div>"
            );
        })
        .join("");
}

function render_prazo_items(prazos) {
    if (!prazos || !prazos.length) return "";
    return prazos
        .map(function (p) {
            var dias = p.dias_restantes;
            var cd = prazo_countdown_label(dias);
            var parts = painel_date_parts(p.data_prazo);
            var card_cls = "painel-schedule-card";
            if (dias < 0) card_cls += " painel-schedule-card--urgent";
            else if (dias <= 1) card_cls += " painel-schedule-card--today";
            return (
                '<div class="' +
                card_cls +
                '" data-dt="Controle de Prazos" data-dn="' +
                frappe.utils.escape_html(p.name) +
                '">' +
                '<div class="painel-schedule-when">' +
                '<span class="painel-schedule-day">' +
                frappe.utils.escape_html(parts.day) +
                "</span>" +
                '<span class="painel-schedule-month">' +
                frappe.utils.escape_html(parts.month) +
                "</span>" +
                '<span class="painel-schedule-countdown ' +
                cd.cls +
                '">' +
                frappe.utils.escape_html(cd.text) +
                "</span></div>" +
                '<div class="painel-schedule-body">' +
                '<div class="painel-schedule-title">' +
                frappe.utils.escape_html(p.descricao || p.name) +
                "</div>" +
                '<div class="painel-schedule-sub">' +
                frappe.utils.escape_html(p.cliente_nome || "—") +
                (p.servico_titulo ? " · " + frappe.utils.escape_html(p.servico_titulo) : "") +
                "</div></div>" +
                '<div class="painel-schedule-meta">' +
                status_pill(p.prioridade || "Normal") +
                "</div></div>"
            );
        })
        .join("");
}

function render_tarefa_items(tarefas) {
    if (!tarefas || !tarefas.length) return "";
    return tarefas
        .map(function (t) {
            var parts = painel_date_parts(t.data_limite);
            var cd = t.data_limite
                ? prazo_countdown_label(t.dias_restantes != null ? t.dias_restantes : 99)
                : { text: __("Sem prazo"), cls: "" };
            var card_cls = "painel-schedule-card";
            if (t.dias_restantes != null && t.dias_restantes < 0) {
                card_cls += " painel-schedule-card--urgent";
            } else if (t.dias_restantes === 0) {
                card_cls += " painel-schedule-card--today";
            }
            return (
                '<div class="' +
                card_cls +
                '" data-dt="Tarefa" data-dn="' +
                frappe.utils.escape_html(t.name) +
                '">' +
                '<div class="painel-schedule-when">' +
                (t.data_limite
                    ? '<span class="painel-schedule-day">' +
                      frappe.utils.escape_html(parts.day) +
                      "</span>" +
                      '<span class="painel-schedule-month">' +
                      frappe.utils.escape_html(parts.month) +
                      "</span>"
                    : '<span class="painel-schedule-day">—</span>') +
                '<span class="painel-schedule-countdown ' +
                cd.cls +
                '">' +
                frappe.utils.escape_html(cd.text) +
                "</span></div>" +
                '<div class="painel-schedule-body">' +
                '<div class="painel-schedule-title">' +
                frappe.utils.escape_html(t.titulo || "") +
                "</div>" +
                '<div class="painel-schedule-sub">' +
                frappe.utils.escape_html(t.responsavel_nome || "—") +
                (t.cliente_nome ? " · " + frappe.utils.escape_html(t.cliente_nome) : "") +
                "</div></div>" +
                '<div class="painel-schedule-meta">' +
                status_pill(t.status) +
                "</div></div>"
            );
        })
        .join("");
}

function painel_icon(name) {
    try {
        return frappe.utils.icon(name, "sm") || "";
    } catch (e) {
        return "";
    }
}

function fmt_currency(val, plain) {
    if (plain) {
        return format_currency(val || 0, "BRL");
    }
    return frappe.format(val || 0, { fieldtype: "Currency", currency: "BRL" });
}

function flt(val) {
    return parseFloat(val) || 0;
}

function fmt_date_iso(iso) {
    if (!iso) return "";
    return frappe.datetime.str_to_user(iso);
}

function fmt_datetime(iso, hora) {
    if (!iso) return "";
    var s = fmt_date_iso(iso);
    if (hora) s += " " + hora;
    return s;
}

function _is_vencido(status) {
    return status === "Vencido";
}

function _pagamento_pode_receber(status) {
    return status === "Pendente" || _is_vencido(status);
}

function status_pill(status) {
    var map = {
        Vencido: "red",
        Pendente: "orange",
        Recebido: "green",
        Repassado: "blue",
        Cancelado: "gray",
        Cancelada: "gray",
        "Em Andamento": "blue",
        Concluída: "green",
        Alta: "red",
        "Média": "orange",
        Media: "orange",
        Virtual: "blue",
        Presencial: "gray",
        Híbrida: "orange",
        Normal: "gray",
        Baixa: "gray",
    };
    var cls = map[status] || "gray";
    return (
        '<span class="indicator-pill ' +
        cls +
        ' filterable no-indicator-dot ellipsis">' +
        frappe.utils.escape_html(status || "") +
        "</span>"
    );
}

function scroll_painel_section(id) {
    var el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

$(document).on("click", ".painel-timeline-item[data-dt], .painel-tl-item[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-prox-card[data-dt], .painel-prox-body[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", "[data-route-calendar]", function (e) {
    e.stopPropagation();
    frappe.set_route("List", "Audiencia", "Calendar");
});

$(document).on("click", ".painel-schedule-item[data-dt], .painel-com-item[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-action-chip", function () {
    var dt = $(this).attr("data-new-dt");
    if (dt) frappe.new_doc(dt);
});

$(document).on("click", ".painel-section-link[data-scroll]", function () {
    scroll_painel_section($(this).attr("data-scroll"));
});

$(document).on("click", "[data-route-list]", function (e) {
    e.stopPropagation();
    var dt = $(this).attr("data-route-list");
    if (dt) painel_goto_list(dt, []);
});

$(document).on("click", ".painel-schedule-card[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-op-item[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", ".painel-parcela-critica", function (e) {
    if ($(e.target).closest(".painel-btn-recebida").length) return;
    var acordo = $(this).attr("data-acordo");
    if (acordo) frappe.set_route("Form", "Acordo de Honorarios Processuais", acordo);
});

$(document).on("click", ".painel-row-acordo", function (e) {
    if ($(e.target).closest(".painel-btn-recebida").length) return;
    var acordo = $(this).attr("data-acordo");
    if (acordo) frappe.set_route("Form", "Acordo de Honorarios Processuais", acordo);
});

$(document).on("click", ".painel-btn-recebida", function (e) {
    e.stopPropagation();
    var btn = $(this);
    var pagamento = btn.attr("data-pagamento") || btn.attr("data-parcela");
    if (!pagamento) return;

    frappe.confirm(
        __("Marcar pagamento como recebido hoje?"),
        function () {
            btn.prop("disabled", true).text("...");
            frappe
                .xcall("advocacia.advocacia.painel_api.marcar_parcela_recebida", {
                    parcela_name: pagamento,
                })
                .then(function () {
                    frappe.show_alert({
                        message: __("Pagamento marcado como Recebido"),
                        indicator: "green",
                    });
                    var page =
                        (frappe.pages.painel && frappe.pages.painel.page) ||
                        (cur_page && cur_page.page ? cur_page.page : null);
                    if (page && typeof load_painel === "function") load_painel(page);
                })
                .catch(function (err) {
                    btn.prop("disabled", false).text("✓ " + __("Recebido"));
                    frappe.msgprint(err.message || __("Erro ao marcar parcela"));
                });
        }
    );
});
