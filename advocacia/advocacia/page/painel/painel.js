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
    page.painel_list_limit = 5;
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
        body.advocacia-painel-active .page-head {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 4px;
        }
        body.advocacia-painel-active .page-head .title-area .title-text {
            visibility: hidden;
            height: 0;
            margin: 0;
            overflow: hidden;
        }
        body.advocacia-painel-active .layout-main-section {
            padding-top: 0;
        }
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
            font-size: var(--text-sm);
            color: var(--text-muted);
            line-height: 1.55;
            max-width: 52rem;
            margin: 0 0 20px;
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
            body.advocacia-painel-active .layout-main-section-wrapper {
                padding-left: 0;
                padding-right: 0;
            }
            body.advocacia-painel-active .page-head {
                padding-left: 12px;
                padding-right: 12px;
            }
            body.advocacia-painel-active .page-head .page-actions .btn {
                min-height: 36px;
                padding: 6px 12px;
                font-size: 12px;
            }
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
            .painel-hero-pulse-stats > span {
                display: block;
                padding: 10px 12px;
                border-radius: var(--painel-radius-sm);
                background: color-mix(in srgb, var(--subtle-fg) 55%, var(--card-bg));
                border: 1px solid color-mix(in srgb, var(--border-color) 55%, transparent);
                font-size: 12px;
                line-height: 1.35;
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
            padding: 14px 16px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 65%, transparent);
            background: color-mix(in srgb, var(--subtle-fg) 35%, var(--card-bg));
        }
        .painel-filtro-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px 12px;
        }
        .painel-periodo-label,
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
            margin-bottom: var(--painel-gap);
        }
        .painel-centro-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        @media (min-width: 640px) {
            .painel-centro-grid { grid-template-columns: repeat(4, 1fr); }
        }
        @media (min-width: 1024px) {
            .painel-centro-grid { grid-template-columns: repeat(6, 1fr); }
        }
        .painel-centro-groups {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .painel-centro-group-title {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin: 0 0 8px;
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
            gap: 10px;
            padding: 12px 14px;
            border-radius: var(--painel-radius-sm);
            border: 1px solid color-mix(in srgb, var(--border-color) 65%, transparent);
            background: var(--card-bg);
            box-shadow: var(--painel-shadow);
            cursor: pointer;
            transition: transform 0.18s ease, box-shadow 0.2s ease;
            min-height: 64px;
        }
        .painel-atencao-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--painel-shadow-hover);
        }
        .painel-atencao-card.tone-red { border-left: 4px solid var(--painel-tone-red); }
        .painel-atencao-card.tone-orange { border-left: 4px solid var(--painel-tone-orange); }
        .painel-atencao-card.tone-yellow { border-left: 4px solid var(--painel-tone-yellow); }
        .painel-atencao-card.tone-green { border-left: 4px solid var(--painel-tone-green); }
        .painel-atencao-card.tone-blue { border-left: 4px solid var(--painel-tone-blue); }
        .painel-atencao-icon {
            flex-shrink: 0;
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: color-mix(in srgb, var(--subtle-fg) 60%, var(--card-bg));
        }
        .painel-atencao-body { flex: 1; min-width: 0; }
        .painel-atencao-count {
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.1;
            color: var(--text-color);
        }
        .painel-atencao-label {
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 3px;
            line-height: 1.3;
            white-space: normal;
            word-break: break-word;
        }
        .painel-atencao-meta {
            font-size: 10px;
            color: var(--text-muted);
            margin-top: 2px;
            line-height: 1.25;
            opacity: 0.9;
        }
        .painel-timeline-list {
            display: flex;
            flex-direction: column;
            gap: 0;
            padding: 8px 0;
        }
        .painel-timeline-item {
            display: grid;
            grid-template-columns: 72px minmax(0, 1fr) auto;
            gap: 10px;
            align-items: start;
            padding: 10px 14px;
            border-bottom: 1px solid color-mix(in srgb, var(--border-color) 45%, transparent);
            cursor: pointer;
            transition: background 0.18s ease;
        }
        .painel-timeline-item:last-child { border-bottom: none; }
        .painel-timeline-item:hover {
            background: color-mix(in srgb, var(--subtle-fg) 50%, var(--card-bg));
        }
        .painel-timeline-date {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            font-variant-numeric: tabular-nums;
        }
        .painel-timeline-type {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-muted);
            margin-bottom: 4px;
        }
        .painel-timeline-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-color);
            line-height: 1.3;
            word-break: break-word;
        }
        .painel-timeline-sub {
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 2px;
            line-height: 1.35;
            word-break: break-word;
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
            .painel-timeline-item {
                grid-template-columns: 72px minmax(0, 1fr);
                grid-template-rows: auto auto;
            }
            .painel-timeline-item .indicator-pill { grid-column: 1 / -1; justify-self: start; }
        }
    `;
    $('<style id="painel-advocacia-styles">' + css + "</style>").appendTo("head");
}

function load_painel(page) {
    mostrar_skeleton(page.painel_container);
    var periodo = page.painel_periodo || 7;
    var list_limit = page.painel_list_limit != null ? page.painel_list_limit : 5;
    frappe.xcall("advocacia.advocacia.painel_api.get_painel_data", {
        periodo_dias: periodo,
        list_limit: list_limit,
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
    filters = filters || [];
    frappe.route_options = null;
    var list_key = "List/" + doctype + "/List";

    var apply_filters = function () {
        var lv = frappe.views.list_view && frappe.views.list_view[list_key];
        if (!lv || !lv.filter_area) return false;
        var tuples = filters.map(function (f) {
            return [doctype, f[0], f[1], f[2]];
        });
        lv.filter_area.clear(false).then(function () {
            if (tuples.length) {
                return lv.filter_area.set(tuples);
            }
        }).then(function () {
            lv.refresh();
        });
        frappe.route_options = null;
        return true;
    };

    var cur = frappe.get_route();
    if (cur[0] === "List" && cur[1] === doctype && apply_filters()) {
        return;
    }

    var attempts = 0;
    var timer = setInterval(function () {
        attempts += 1;
        if (apply_filters() || attempts > 30) {
            clearInterval(timer);
        }
    }, 100);
    frappe.set_route("List", doctype);
}

function render_painel($container, d, page) {
    var periodo = d.periodo_dias || page.painel_periodo || 7;
    var list_limit = d.list_limit != null ? d.list_limit : page.painel_list_limit || 5;
    var meta = d.list_meta || {};
    page.painel_list_limit = list_limit;
    var html = '<div class="painel-content">';
    html += render_header(d.resumo, d.kpis, periodo, d.financeiro);
    html += render_filtros_painel(periodo, list_limit);
    html += render_acoes_rapidas();
    html += render_centro_atencao(
        d.centro_atencao,
        d.kpis,
        d.financeiro,
        d.horas_periodo != null ? d.horas_periodo : d.horas_semana,
        d.total_despesas_mes,
        periodo
    );
    html += render_timeline(d.timeline, periodo, meta.timeline, list_limit);
    html += render_comunicacoes_pendentes(
        d.comunicacoes_pendentes || d.ultimas_comunicacoes,
        periodo,
        meta.comunicacoes,
        list_limit
    );
    html += render_financeiro(d.financeiro, periodo);
    html += render_duo_honorarios_despesas(
        d.parcelas,
        d.despesas_pendentes,
        d.total_despesas_mes,
        meta.parcelas,
        meta.despesas,
        list_limit
    );
    html += render_duo_custas_horas(
        d.custas_pendentes_repasse,
        d.total_custas_mes,
        d.horas_periodo != null ? d.horas_periodo : d.horas_semana,
        meta.custas,
        periodo,
        list_limit
    );
    html += "</div>";
    $container.html(html);
    bind_painel_filters($container, page);
    bind_atencao_routes($container, page);
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

function painel_context_line(resumo, kpis, periodo_dias, financeiro) {
    resumo = resumo || {};
    kpis = kpis || {};
    financeiro = financeiro || {};
    periodo_dias = cint(periodo_dias) || 7;
    if (resumo.urgencia !== "alta") {
        return __("Visão operacional {0} — nenhuma urgência crítica no radar.", [
            painel_periodo_enunciado(periodo_dias),
        ]);
    }
    var parts = [];
    if (resumo.audiencias_hoje) {
        parts.push(
            __("{0} audiência(s) hoje exigem presença ou preparo", [resumo.audiencias_hoje])
        );
    }
    if (resumo.parcelas_vencidas) {
        parts.push(__("{0} parcela(s) vencida(s) aguardam recebimento", [resumo.parcelas_vencidas]));
    }
    if (resumo.prazos_urgentes) {
        parts.push(__("{0} prazo(s) com vencimento iminente", [resumo.prazos_urgentes]));
    }
    var previsto =
        (financeiro.previsto_periodo && financeiro.previsto_periodo.valor) ||
        resumo.previsto_periodo_valor ||
        0;
    if (previsto) {
        parts.push(
            __("{0}: {1}", [
                painel_periodo_previsto_label(periodo_dias),
                fmt_currency(previsto, true),
            ])
        );
    }
    return parts.join(". ") + ".";
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
        '<span><strong>' +
        (resumo.audiencias_hoje || 0) +
        "</strong> " +
        __("audiência(s) hoje") +
        "</span><span><strong>" +
        (resumo.parcelas_vencidas || 0) +
        "</strong> " +
        __("parcela(s) vencida(s)") +
        "</span><span><strong>" +
        fmt_currency(previsto_val, true) +
        "</strong> " +
        painel_periodo_previsto_label(periodo_dias) +
        "</span>";
    if (resumo.prazos_urgentes) {
        pulse_stats +=
            "<span><strong>" +
            resumo.prazos_urgentes +
            "</strong> " +
            __("prazo(s) crítico(s)") +
            "</span>";
    }
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
        frappe.utils.escape_html(painel_context_line(resumo, kpis, periodo_dias, financeiro)) +
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

function render_filtros_painel(periodo_atual, list_limit) {
    var opcoes_periodo = [
        { dias: 1, label: __("Hoje") },
        { dias: 7, label: __("7 dias") },
        { dias: 15, label: __("15 dias") },
        { dias: 30, label: __("30 dias") },
    ];
    var opcoes_linhas = [
        { val: 5, label: "5" },
        { val: 10, label: "10" },
        { val: 15, label: "15" },
        { val: 0, label: __("Todos") },
    ];
    list_limit = list_limit != null ? cint(list_limit) : 5;
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
    h +=
        "</div></div>" +
        '<div class="painel-filtro-group">' +
        '<span class="painel-linhas-label">' +
        __("Itens por lista") +
        "</span>" +
        '<div class="painel-linhas-filters">';
    opcoes_linhas.forEach(function (op) {
        h +=
            '<button type="button" class="painel-linhas-btn' +
            (list_limit === op.val ? " active" : "") +
            '" data-linhas="' +
            op.val +
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

    var indicadores = [
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

    return (
        '<section class="painel-section painel-centro-atencao" id="painel-centro-atencao">' +
        '<div class="painel-section-head"><div><h2 class="painel-section-title">' +
        __("Centro de Atenção") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Urgências e indicadores {0}", [painel_periodo_enunciado(periodo_dias)]) +
        "</p></div></div>" +
        '<div class="painel-centro-groups">' +
        group(__("Urgente"), urgentes) +
        group(__("No período ({0})", [painel_periodo_label(periodo_dias)]), no_periodo) +
        group(__("Indicadores"), indicadores) +
        "</div></section>"
    );
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
        '<section class="painel-section painel-section--timeline" id="painel-timeline"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        titulo +
        "</h2>" +
        '<p class="painel-section-sub">' +
        subtitulo +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
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

    h += '<div class="painel-panel"><div class="painel-timeline-list">';
    timeline.forEach(function (it) {
        var tipo_label =
            it.tipo === "audiencia"
                ? __("Audiência")
                : it.tipo === "prazo"
                  ? __("Prazo")
                  : __("Tarefa");
        var pill_map = { red: "Alta", orange: "Média", yellow: "Normal", blue: "Normal", gray: "Baixa" };
        h +=
            '<div class="painel-timeline-item" data-dt="' +
            frappe.utils.escape_html(it.doctype || "") +
            '" data-dn="' +
            frappe.utils.escape_html(it.docname || "") +
            '">' +
            '<div class="painel-timeline-date">' +
            frappe.utils.escape_html(fmt_date_iso(it.data)) +
            (it.hora ? " · " + frappe.utils.escape_html(it.hora) : "") +
            "</div>" +
            '<div class="painel-timeline-body">' +
            '<div class="painel-timeline-type">' +
            painel_icon(it.tipo === "audiencia" ? "milestone" : it.tipo === "prazo" ? "time" : "checklist") +
            frappe.utils.escape_html(tipo_label) +
            "</div>" +
            '<div class="painel-timeline-title">' +
            frappe.utils.escape_html(it.titulo || "") +
            "</div>" +
            '<div class="painel-timeline-sub">' +
            frappe.utils.escape_html(it.subtitulo || "") +
            (it.detalhe ? " · " + frappe.utils.escape_html(it.detalhe) : "") +
            "</div></div>" +
            status_pill(pill_map[it.urgencia] || "Normal") +
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
        '<section class="painel-section" id="painel-comunicacoes"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Comunicações") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Follow-ups pendentes — visão {0}", [painel_periodo_enunciado(periodo_dias)]) +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
        meta_html +
        '<span class="painel-section-link" data-route-list="Comunicacao">' +
        __("Ver todas") +
        "</span></div></div>";

    if (!comunicacoes || !comunicacoes.length) {
        return (
            h +
            '<div class="painel-panel">' +
            render_empty_state(
                "message",
                __("Nenhuma comunicação pendente"),
                __("Retornos e follow-ups aparecerão aqui quando precisarem de ação.")
            ) +
            "</div></section>"
        );
    }

    h += '<div class="painel-panel"><div class="painel-schedule-list">';
    comunicacoes.forEach(function (c) {
        var urg = c.urgencia_ordem === 0 ? "red" : c.urgencia_ordem === 1 ? "orange" : "yellow";
        h +=
            '<div class="painel-schedule-item" data-comunicacao="' +
            frappe.utils.escape_html(c.name || "") +
            '" data-dt="Comunicacao" data-dn="' +
            frappe.utils.escape_html(c.name || "") +
            '">' +
            '<div class="painel-schedule-main">' +
            '<div class="painel-op-title">' +
            frappe.utils.escape_html(c.assunto || c.name) +
            "</div>" +
            '<div class="painel-op-sub">' +
            frappe.utils.escape_html(c.cliente || "") +
            (c.motivo_pendencia ? " · " + frappe.utils.escape_html(c.motivo_pendencia) : "") +
            "</div></div>" +
            '<div class="painel-schedule-side">' +
            status_pill(urg === "red" ? "Alta" : urg === "orange" ? "Média" : "Normal") +
            '<span class="painel-op-sub">' +
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
        var linhas = cint($(this).attr("data-linhas"));
        if (!page || linhas === page.painel_list_limit) return;
        page.painel_list_limit = linhas;
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

function get_kpi_routes() {
    var hoje = frappe.datetime.get_today();
    var mes_inicio = frappe.datetime.month_start(hoje);
    var mes_fim = frappe.datetime.month_end(hoje);
    var tres_dias = frappe.datetime.add_days(hoje, 3);

    return [
        function () {
            frappe.route_options = { status: "Vencido" };
            frappe.set_route("List", "Pagamento");
        },
        function () {
            frappe.route_options = {
                status: ["in", ["Recebido", "Repassado"]],
                data_recebimento: ["between", [mes_inicio, mes_fim]],
            };
            frappe.set_route("List", "Pagamento");
        },
        function () {
            frappe.route_options = {
                status: "Pendente",
                data_vencimento: ["between", [mes_inicio, mes_fim]],
            };
            frappe.set_route("List", "Pagamento");
        },
        function () {
            frappe.route_options = {
                data_hora: ["between", [hoje + " 00:00:00", hoje + " 23:59:59"]],
            };
            frappe.set_route("List", "Audiencia");
        },
        function () {
            frappe.route_options = {
                status: "Pendente",
                data_prazo: ["<=", tres_dias],
            };
            frappe.set_route("List", "Controle de Prazos");
        },
        function () {
            frappe.route_options = { status: "Em andamento" };
            frappe.set_route("List", "Servico");
        },
    ];
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

function bind_kpi_routes($root, routes) {
    $root.find(".painel-kpi").each(function (idx) {
        $(this)
            .off("click")
            .on("click", function () {
                if (routes[idx]) routes[idx]();
            });
    });
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
                (a.cliente ? a.cliente + " · " : "") +
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
            sub: (a.cliente || "") + (a.vara_label ? " · " + a.vara_label : ""),
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
                    __("Recebida") +
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

function render_duo_honorarios_despesas(parcelas, despesas, total_mes, meta_parcelas, meta_despesas, list_limit) {
    return (
        '<div class="painel-duo-grid" id="painel-duo-financeiro">' +
        render_parcelas(parcelas, true, meta_parcelas, list_limit) +
        render_despesas(despesas, total_mes, true, meta_despesas, list_limit) +
        "</div>"
    );
}

function render_duo_custas_horas(custas, total_mes, horas, meta_custas, periodo_dias, list_limit) {
    return (
        '<div class="painel-duo-grid" id="painel-duo-secundario">' +
        render_custas(custas, total_mes, true, meta_custas, list_limit) +
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
    return (
        '<section class="painel-section" id="painel-financeiro"><div class="painel-section-head">' +
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
        '</div><div class="painel-chart">' +
        chart_rows +
        "</div></div></div></section>"
    );
}

function render_parcelas(parcelas, compact, list_meta, list_limit) {
    var meta_html = painel_list_meta_html(list_meta, list_limit);
    var h =
        '<section class="painel-section' +
        (compact ? " painel-section--nested" : "") +
        '" id="painel-parcelas"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Honorários em aberto") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Pendentes e vencidos") +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
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
                __("Recebida") +
                "</button>";
        }
        h +=
            '<div class="painel-parcela-card painel-row-acordo" data-acordo="' +
            frappe.utils.escape_html(p.parent || "") +
            '">' +
            '<div class="painel-parcela-main"><div class="painel-op-title">' +
            frappe.utils.escape_html(p.cliente_nome || "—") +
            '</div><div class="painel-op-sub">' +
            frappe.utils.escape_html(p.servico_titulo || p.servico_tipo || "") +
            (p.numero_processo ? " · " + frappe.utils.escape_html(p.numero_processo) : "") +
            "</div></div>" +
            '<div class="painel-parcela-valor">' +
            fmt_currency(p.valor_total) +
            "</div>" +
            '<div class="painel-muted">' +
            fmt_date_iso(p.vencimento) +
            (prazo_txt ? " · " + prazo_txt : "") +
            "</div>" +
            status_pill(p.status) +
            btn +
            "</div>";
    });
    h += "</div></section>";
    return h;
}

function render_despesas(despesas, total_mes, compact, list_meta, list_limit) {
    var meta_html = painel_list_meta_html(list_meta, list_limit);
    var h =
        '<section class="painel-section' +
        (compact ? " painel-section--nested" : "") +
        '" id="painel-despesas"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Despesas") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Pendentes · mês calendário: {0}", [fmt_currency(total_mes || 0, true)]) +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
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
            '<div class="painel-schedule-item painel-row-despesa" data-despesa="' +
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
            "</div></div>" +
            '<div class="painel-schedule-side">' +
            badge +
            '<div class="painel-op-valor ' +
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
        (compact ? " painel-section--nested" : "") +
        '" id="painel-custas"><div class="painel-section-head">' +
        "<div><h2 class='painel-section-title'>" +
        __("Custas") +
        "</h2>" +
        '<p class="painel-section-sub">' +
        __("Repasse · mês calendário: {0}", [fmt_currency(total_mes || 0, true)]) +
        "</p></div>" +
        '<div class="painel-section-head-actions">' +
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
            '<div class="painel-schedule-item" data-custa="' +
            frappe.utils.escape_html(c.name || "") +
            '">' +
            '<div class="painel-schedule-main">' +
            '<div class="painel-op-title">' +
            frappe.utils.escape_html(c.descricao || c.name) +
            "</div>" +
            '<div class="painel-op-sub">' +
            frappe.utils.escape_html(c.tipo || "") +
            (c.servico ? " · " + frappe.utils.escape_html(c.servico) : "") +
            "</div></div>" +
            '<div class="painel-schedule-side">' +
            '<span class="indicator-pill blue">' + __("Aguardando repasse") + "</span>" +
            '<div class="painel-op-valor warn">' +
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
        (compact ? " painel-section--nested" : " painel-section--inline") +
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
            (c.cliente ? " · " + frappe.utils.escape_html(c.cliente) : "") +
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
                frappe.utils.escape_html(a.cliente || "—") +
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
    return status === "Vencida" || status === "Vencido";
}

function _pagamento_pode_receber(status) {
    return status === "Pendente" || _is_vencido(status);
}

function status_pill(status) {
    var map = {
        Vencida: "red",
        Vencido: "red",
        Pendente: "orange",
        Recebida: "green",
        Recebido: "green",
        Repassada: "blue",
        Repassado: "blue",
        Cancelada: "gray",
        Cancelado: "gray",
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

$(document).on("click", ".painel-timeline-item[data-dt]", function (e) {
    if ($(e.target).closest(".painel-btn-recebida, .painel-btn-entrar").length) return;
    var dt = $(this).attr("data-dt");
    var dn = $(this).attr("data-dn");
    if (dt && dn) frappe.set_route("Form", dt, dn);
});

$(document).on("click", "[data-route-calendar]", function (e) {
    e.stopPropagation();
    frappe.set_route("List", "Audiencia", "Calendar");
});

$(document).on("click", ".painel-schedule-item[data-dt]", function (e) {
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
                    btn.prop("disabled", false).text("✓ " + __("Recebida"));
                    frappe.msgprint(err.message || __("Erro ao marcar parcela"));
                });
        }
    );
});
