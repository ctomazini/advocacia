#!/usr/bin/env node
/**
 * Sessão E2E Playwright — app advocacia.
 * Login + frappe.db.insert no Desk autenticado; visita /app/painel ao final.
 */
import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const E2E_ROOT = path.dirname(fileURLToPath(import.meta.url));

const BASE = process.env.E2E_BASE_URL || "http://127.0.0.1:8000";
const SITE_HOST = process.env.E2E_SITE_HOST || "advocacia.local";
const USER = process.env.E2E_USER || "Administrator";
const PASS = process.env.E2E_PASS || "";
const RUN_ID = Date.now().toString(36);
const MARKER = `PLAYWRIGHT_${RUN_ID}`;

const OUT_DIR = process.env.E2E_OUT_DIR || path.join(E2E_ROOT, "results", RUN_ID);
fs.mkdirSync(OUT_DIR, { recursive: true });

const results = [];
const created = {};

function log(step, status, detail = "") {
	results.push({ step, status, detail, at: new Date().toISOString() });
	console.log(`${status === "ok" ? "✓" : "✗"} ${step}${detail ? ` — ${detail}` : ""}`);
}

function calcCpfDv(base) {
	let sum = 0;
	for (let i = 0; i < 9; i++) sum += parseInt(base[i], 10) * (10 - i);
	let d1 = 11 - (sum % 11);
	if (d1 >= 10) d1 = 0;
	sum = 0;
	const b10 = base + d1;
	for (let i = 0; i < 10; i++) sum += parseInt(b10[i], 10) * (11 - i);
	let d2 = 11 - (sum % 11);
	if (d2 >= 10) d2 = 0;
	return `${d1}${d2}`;
}

function randomCpf() {
	let base;
	do {
		base = Array.from({ length: 9 }, () => Math.floor(Math.random() * 10)).join("");
	} while (new Set(base).size === 1);
	return base + calcCpfDv(base);
}

function slug(doctype) {
	return doctype.toLowerCase().replace(/ /g, "-");
}

async function waitDesk(page) {
	await page.waitForFunction(() => window.frappe?.boot && frappe.session?.user !== "Guest", null, {
		timeout: 60000,
	});
	await page.waitForTimeout(400);
}

async function visitNewForm(page, doctype) {
	await page.goto(`${BASE}/app/${slug(doctype)}/new`, { waitUntil: "domcontentloaded" });
	await waitDesk(page);
	await page.waitForSelector(".form-layout", { timeout: 60000 });
}

async function visitDoc(page, doctype, name) {
	await page.goto(`${BASE}/app/${slug(doctype)}/${encodeURIComponent(name)}`, {
		waitUntil: "domcontentloaded",
	});
	await waitDesk(page);
}

async function insertDoc(page, doc) {
	const result = await page.evaluate(async (payload) => {
		try {
			const inserted = await frappe.db.insert(payload);
			return { ok: true, name: inserted.name };
		} catch (e) {
			return {
				ok: false,
				error: e?.message || e?.exc || String(e),
				server: frappe.last_response?._server_messages || "",
			};
		}
	}, doc);
	if (!result?.ok) {
		throw new Error(`${result?.error || "insert failed"} ${result?.server || ""}`.trim());
	}
	return result.name;
}

async function runStep(page, name, fn) {
	try {
		const detail = await fn();
		log(name, "ok", detail || "");
		return true;
	} catch (err) {
		log(name, "fail", (err?.message || String(err)).slice(0, 280));
		await page
			.screenshot({ path: path.join(OUT_DIR, `${name.replace(/\W+/g, "_")}.png`), fullPage: true })
			.catch(() => {});
		return false;
	}
}

async function main() {
	if (!PASS) {
		console.error("Defina E2E_PASS com a senha do usuário de teste.");
		process.exit(1);
	}

	const state = {
		jurisdiction: `${MARKER} Comarca`,
		court: `${MARKER} Tribunal`,
		courtBranch: `${MARKER} Vara`,
		casePhase: `${MARKER} Fase`,
		clientCpf: randomCpf(),
		clientName: `${MARKER} Cliente`,
		legalCase: null,
	};

	const browser = await chromium.launch({ headless: true });
	const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
	await page.route("**/*", async (route) => {
		await route.continue({ headers: { ...route.request().headers(), host: SITE_HOST } });
	});

	await runStep(page, "login", async () => {
		await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
		await page.fill("#login_email", USER);
		await page.fill("#login_password", PASS);
		await page.click(".btn-login");
		await page.waitForURL(/\/(app|desk)/, { timeout: 60000 });
		await waitDesk(page);
		return USER;
	});

	await runStep(page, "jurisdiction", async () => {
		await visitNewForm(page, "Jurisdiction");
		const name = await insertDoc(page, {
			doctype: "Jurisdiction",
			jurisdiction_name: state.jurisdiction,
			uf: "SP",
			city: "Sao Paulo",
		});
		created["Jurisdiction"] = name;
		return name;
	});

	await runStep(page, "court", async () => {
		await visitNewForm(page, "Court");
		const name = await insertDoc(page, {
			doctype: "Court",
			court_name: state.court,
			abbreviation: `PW${RUN_ID.slice(-4)}`,
			jurisdiction: "Estadual",
		});
		created["Court"] = name;
		return name;
	});

	await runStep(page, "court-branch", async () => {
		await visitNewForm(page, "Court Branch");
		const name = await insertDoc(page, {
			doctype: "Court Branch",
			court_branch_name: state.courtBranch,
			jurisdiction: state.jurisdiction,
			court_type: "Cível",
		});
		created["Court Branch"] = name;
		return name;
	});

	await runStep(page, "case-phase", async () => {
		await visitNewForm(page, "Case Phase");
		const name = await insertDoc(page, {
			doctype: "Case Phase",
			case_phase_name: state.casePhase,
			sort_order: 99,
		});
		created["Case Phase"] = name;
		return name;
	});

	await runStep(page, "client", async () => {
		await visitNewForm(page, "Client");
		const name = await insertDoc(page, {
			doctype: "Client",
			person_type: "Pessoa Física",
			client_name: state.clientName,
			cpf: state.clientCpf,
		});
		created["Client"] = name;
		return name;
	});

	await runStep(page, "legal-case", async () => {
		await visitNewForm(page, "Legal Case");
		state.legalCase = await insertDoc(page, {
			doctype: "Legal Case",
			client: created["Client"],
			type: "Processo Judicial",
			area: "Cível",
			status: "Em andamento",
			case_phase: state.casePhase,
			remarks: `${MARKER} processo E2E`,
		});
		created["Legal Case"] = state.legalCase;
		await visitDoc(page, "Legal Case", state.legalCase);
		return state.legalCase;
	});

	await runStep(page, "deadline", async () => {
		await visitNewForm(page, "Deadline");
		const due = new Date(Date.now() + 86400000 * 7).toISOString().slice(0, 10);
		const name = await insertDoc(page, {
			doctype: "Deadline",
			legal_case: state.legalCase,
			client: created["Client"],
			description: `${MARKER} prazo`,
			due_date: due,
			status: "Pendente",
		});
		created["Deadline"] = name;
		return name;
	});

	await runStep(page, "hearing", async () => {
		await visitNewForm(page, "Hearing");
		const when = new Date(Date.now() + 86400000 * 14).toISOString().slice(0, 19).replace("T", " ");
		const name = await insertDoc(page, {
			doctype: "Hearing",
			legal_case: state.legalCase,
			client: created["Client"],
			type: "Instrução",
			modality: "Virtual",
			hearing_datetime: when,
			status: "Agendada",
		});
		created["Hearing"] = name;
		return name;
	});

	await runStep(page, "painel", async () => {
		await page.goto(`${BASE}/app/painel`, { waitUntil: "domcontentloaded" });
		await waitDesk(page);
		await page.waitForSelector(".painel-root, .advocacia-painel-active", { timeout: 60000 });
		return "/app/painel";
	});

	await browser.close();

	const report = {
		marker: MARKER,
		created,
		results,
		finished_at: new Date().toISOString(),
	};
	fs.writeFileSync(path.join(OUT_DIR, "report.json"), JSON.stringify(report, null, 2));

	const failed = results.filter((r) => r.status === "fail").length;
	console.log(`\nE2E concluído — ${results.length - failed}/${results.length} OK`);
	console.log(`Relatório: ${path.join(OUT_DIR, "report.json")}`);
	process.exit(failed ? 1 : 0);
}

main().catch((err) => {
	console.error(err);
	process.exit(1);
});
