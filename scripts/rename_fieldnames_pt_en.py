"""Reescreve os DocType JSONs aplicando o rename de fieldnames PT→EN.

Fonte do mapa: advocacia/patches/v16_0/rename_fields_pt_en.py (RENAMES).
Re-executável (idempotente). Uso:
	python3 scripts/rename_fieldnames_pt_en.py
"""

import ast
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCTYPE_DIR = REPO / "advocacia" / "advocacia" / "doctype"
MAP_FILE = REPO / "advocacia" / "patches" / "v16_0" / "rename_fields_pt_en.py"

# Referências já quebradas nos JSONs, corrigidas junto com o rename
FETCH_FROM_FIXES = {"servico.cliente": "legal_case.client"}
DEPENDS_ON_FIXES = {"eval:doc.tarefa": "eval:doc.generate_task"}
SEARCH_FIELD_FIXES = {"cliente": "client", "comarca": "jurisdiction"}
# field_order com nomes da era pré-rename de DocTypes (PT) — alinhar aos fields atuais
STALE_ORDER_FIXES = {
	"servico": "legal_case",
	"cliente": "client",
	"tarefa": "legal_task",
	"local_vara": "court_branch",
	"acordo": "fee_agreement",
	"registro_atos": "service_record",
}


def load_renames() -> dict[str, dict[str, str]]:
	tree = ast.parse(MAP_FILE.read_text())
	for node in ast.walk(tree):
		if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "RENAMES":
			return ast.literal_eval(node.value)
		if isinstance(node, ast.Assign) and any(
			getattr(t, "id", "") == "RENAMES" for t in node.targets
		):
			return ast.literal_eval(node.value)
	raise RuntimeError("RENAMES não encontrado em rename_fields_pt_en.py")


def map_eval_expr(expr: str, renames: dict[str, str]) -> str:
	if expr in DEPENDS_ON_FIXES:
		return DEPENDS_ON_FIXES[expr]
	for old, new in sorted(renames.items(), key=lambda kv: -len(kv[0])):
		expr = re.sub(rf"\bdoc\.{old}\b", f"doc.{new}", expr)
	return expr


def map_field_list(value: str, renames: dict[str, str]) -> str:
	tokens = [t.strip() for t in value.split(",") if t.strip()]
	out = []
	for t in tokens:
		t = renames.get(t, SEARCH_FIELD_FIXES.get(t, t))
		out.append(t)
	return ",".join(out)


def process_doctype(path: Path, renames_all: dict[str, dict[str, str]]) -> bool:
	doc = json.loads(path.read_text())
	if doc.get("doctype") != "DocType":
		return False
	renames = renames_all.get(doc.get("name"), {})

	changed = json.dumps(doc, sort_keys=True)

	if doc.get("field_order"):
		doc["field_order"] = [
			renames.get(f, STALE_ORDER_FIXES.get(f, f)) for f in doc["field_order"]
		]

	for f in doc.get("fields", []):
		fn = f.get("fieldname")
		if fn in renames:
			f["fieldname"] = renames[fn]
		for attr in ("depends_on", "mandatory_depends_on", "read_only_depends_on"):
			if f.get(attr):
				f[attr] = map_eval_expr(f[attr], renames)
		if f.get("fetch_from"):
			ff = f["fetch_from"]
			if ff in FETCH_FROM_FIXES:
				f["fetch_from"] = FETCH_FROM_FIXES[ff]
			else:
				link_field, _, remote = ff.partition(".")
				link_field = renames.get(link_field, link_field)
				# resolve doctype remoto pelo Link local
				remote_dt = next(
					(
						x.get("options")
						for x in doc.get("fields", [])
						if x.get("fieldname") == link_field and x.get("fieldtype") == "Link"
					),
					None,
				)
				remote = renames_all.get(remote_dt, {}).get(remote, remote)
				f["fetch_from"] = f"{link_field}.{remote}"

	for attr in ("title_field", "sort_field"):
		if doc.get(attr) in renames:
			doc[attr] = renames[doc[attr]]
	if doc.get("search_fields"):
		doc["search_fields"] = map_field_list(doc["search_fields"], renames)
	autoname = doc.get("autoname") or ""
	if autoname.startswith("field:"):
		fld = autoname[len("field:"):]
		if fld in renames:
			doc["autoname"] = f"field:{renames[fld]}"

	for link in doc.get("links", []):
		remote_dt = link.get("link_doctype")
		lf = link.get("link_fieldname")
		if lf and remote_dt in renames_all:
			link["link_fieldname"] = renames_all[remote_dt].get(lf, lf)

	if json.dumps(doc, sort_keys=True) == changed:
		return False
	path.write_text(json.dumps(doc, indent=1, ensure_ascii=False, sort_keys=False) + "\n")
	return True


def main() -> None:
	renames_all = load_renames()
	touched = []
	for path in sorted(DOCTYPE_DIR.glob("*/*.json")):
		if process_doctype(path, renames_all):
			touched.append(path.name)
	print(f"{len(touched)} JSONs alterados:")
	for name in touched:
		print(f"  {name}")


if __name__ == "__main__":
	main()
