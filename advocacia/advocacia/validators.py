"""Validações regulatórias brasileiras (CPF, CNPJ, CNJ, telefone, e-mail)."""

import re
from datetime import datetime

import frappe
from frappe import _

# DDDs geográficos válidos (ANATEL)
DDDS_VALIDOS = frozenset({
	"11", "12", "13", "14", "15", "16", "17", "18", "19",
	"21", "22", "24", "27", "28",
	"31", "32", "33", "34", "35", "37", "38",
	"41", "42", "43", "44", "45", "46", "47", "48", "49",
	"51", "53", "54", "55",
	"61", "62", "63", "64", "65", "66", "67", "68", "69",
	"71", "73", "74", "75", "77", "79",
	"81", "82", "83", "84", "85", "86", "87", "88", "89",
	"91", "92", "93", "94", "95", "96", "97", "98", "99",
})


def limpar_numerico(valor):
	"""Remove tudo que não é dígito e retorna string (vazia se valor nulo)."""
	if valor is None:
		return ""
	return re.sub(r"\D", "", str(valor))


def limpar_cnpj(valor):
	"""Normaliza CNPJ: remove máscara, 12 chars A-Z/0-9 + DV só dígitos, maiúsculas."""
	if valor is None:
		return ""
	raw = re.sub(r"[^0-9A-Za-z]", "", str(valor)).upper()
	body = raw[:12]
	dv = re.sub(r"[^0-9]", "", raw[12:])[:2]
	return body + dv


def formatar_cpf(cpf):
	"""Exibição mascarada; aceita valor já limpo do banco."""
	cpf = limpar_numerico(cpf)
	if len(cpf) != 11:
		return cpf
	return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_cnpj(cnpj):
	"""Exibição mascarada; aceita CNPJ numérico ou alfanumérico (14 chars)."""
	cnpj = limpar_cnpj(cnpj)
	if len(cnpj) != 14:
		return cnpj
	return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def formatar_telefone(numero):
	"""Exibição mascarada; infere fixo (10) ou celular (11) pelo tamanho."""
	numero = limpar_numerico(numero)
	if len(numero) == 11:
		return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"
	if len(numero) == 10:
		return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
	return numero


def formatar_cep(cep):
	cep = limpar_numerico(cep)
	if len(cep) != 8:
		return cep
	return f"{cep[:5]}-{cep[5:]}"


def formatar_cnj(numero):
	"""Exibição mascarada do número CNJ (20 dígitos)."""
	numero = limpar_numerico(numero)
	if len(numero) != 20:
		return numero
	return (
		f"{numero[0:7]}-{numero[7:9]}.{numero[9:13]}.{numero[13]}."
		f"{numero[14:16]}.{numero[16:20]}"
	)


def _sequencia_repetida(digitos):
	return len(set(digitos)) == 1


def _calcular_dv_cpf(cpf_base):
	"""Calcula os dois dígitos verificadores do CPF (base com 9 dígitos)."""
	soma = sum(int(cpf_base[i]) * (10 - i) for i in range(9))
	resto = (soma * 10) % 11
	d1 = 0 if resto == 10 else resto
	soma = sum(int(cpf_base[i]) * (11 - i) for i in range(9)) + d1 * 2
	resto = (soma * 10) % 11
	d2 = 0 if resto == 10 else resto
	return f"{d1}{d2}"


def validar_cpf(cpf):
	"""
	Valida CPF pela Receita Federal: limpa, rejeita sequências repetidas,
	confere dígitos verificadores. Retorna apenas dígitos ou lança erro.
	"""
	cpf = limpar_numerico(cpf)
	if not cpf:
		return cpf
	if len(cpf) != 11:
		frappe.throw(_("CPF deve conter 11 dígitos."), title=_("CPF inválido"))
	if _sequencia_repetida(cpf):
		frappe.throw(_("CPF inválido (sequência repetida)."), title=_("CPF inválido"))
	if cpf[-2:] != _calcular_dv_cpf(cpf[:9]):
		frappe.throw(_("CPF inválido (dígitos verificadores incorretos)."), title=_("CPF inválido"))
	return cpf


def _valor_ascii_cnpj(char: str) -> int:
	"""Converte caractere CNPJ para valor numérico (Receita: ASCII − 48)."""
	return ord(char) - 48


def _calcular_dv_cnpj(cnpj_base):
	"""Calcula os dois DVs do CNPJ (base com 12 chars A-Z/0-9). Módulo 11 + ASCII−48."""
	pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
	pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
	soma = sum(_valor_ascii_cnpj(cnpj_base[i]) * pesos1[i] for i in range(12))
	d1 = 11 - (soma % 11)
	d1 = 0 if d1 >= 10 else d1
	base13 = cnpj_base + str(d1)
	soma = sum(_valor_ascii_cnpj(base13[i]) * pesos2[i] for i in range(13))
	d2 = 11 - (soma % 11)
	d2 = 0 if d2 >= 10 else d2
	return f"{d1}{d2}"


def validar_cnpj(cnpj):
	"""
	Valida CNPJ numérico ou alfanumérico (Receita Federal).
	Retorna 14 chars sem máscara (A-Z/0-9) ou lança erro.
	"""
	cnpj = limpar_cnpj(cnpj)
	if not cnpj:
		return cnpj
	if len(cnpj) != 14:
		frappe.throw(_("CNPJ deve conter 14 caracteres."), title=_("CNPJ inválido"))
	raiz_ordem, dv = cnpj[:12], cnpj[12:]
	if not re.fullmatch(r"[0-9A-Z]{12}", raiz_ordem):
		frappe.throw(
			_("As 12 primeiras posições do CNPJ devem ser letras (A-Z) ou dígitos."),
			title=_("CNPJ inválido"),
		)
	if not dv.isdigit() or len(dv) != 2:
		frappe.throw(
			_("Os 2 últimos caracteres do CNPJ (dígitos verificadores) devem ser números (0-9)."),
			title=_("CNPJ inválido"),
		)
	if _sequencia_repetida(cnpj):
		frappe.throw(_("CNPJ inválido (sequência repetida)."), title=_("CNPJ inválido"))
	if dv != _calcular_dv_cnpj(raiz_ordem):
		frappe.throw(_("CNPJ inválido (dígitos verificadores incorretos)."), title=_("CNPJ inválido"))
	return cnpj


def _calcular_dv_cnj(numero_20):
	"""
	Dígito verificador CNJ — Módulo 97 Base 10 (Resolução CNJ 65/2008, Anexo VIII).
	numero_20: string com 20 dígitos (inclui DV nas posições 8-9).
	"""
	base = numero_20[0:7] + numero_20[9:20]
	resto = int(base + "00") % 97
	return str(98 - resto).zfill(2)


def validar_cnj(numero):
	"""
	Valida número CNJ: 20 dígitos, DV módulo 97, ano entre 1900 e o ano atual.
	Retorna string só com dígitos ou lança erro.
	"""
	numero = limpar_numerico(numero)
	if not numero:
		return numero
	if len(numero) != 20:
		frappe.throw(
			_("Número CNJ deve conter exatamente 20 dígitos."),
			title=_("CNJ inválido"),
		)
	dv_informado = numero[7:9]
	dv_calculado = _calcular_dv_cnj(numero)
	if dv_informado != dv_calculado:
		frappe.throw(
			_("Número CNJ inválido (dígitos verificadores incorretos)."),
			title=_("CNJ inválido"),
		)
	try:
		ano = int(numero[9:13])
	except ValueError:
		frappe.throw(_("Ano do processo CNJ inválido."), title=_("CNJ inválido"))
	ano_atual = datetime.now().year
	if ano < 1900:
		frappe.throw(_("Ano do processo CNJ não pode ser anterior a 1900."), title=_("CNJ inválido"))
	if ano > ano_atual:
		frappe.throw(
			_("Ano do processo CNJ não pode ser superior ao ano atual ({0}).").format(ano_atual),
			title=_("CNJ inválido"),
		)
	return numero


def validar_telefone(numero, phone_type="mobile"):
	"""
	Valida telefone brasileiro (ANATEL): DDD geográfico, celular 11 dígitos
	(nono dígito 9, segundo dígito do número não 0/1) ou fixo 10 dígitos
	(primeiro dígito local entre 2 e 5). Retorna só dígitos ou lança erro.
	"""
	numero = limpar_numerico(numero)
	if not numero:
		return numero

	if len(numero) < 10:
		frappe.throw(_("Telefone incompleto."), title=_("Telefone inválido"))

	ddd = numero[:2]
	if ddd not in DDDS_VALIDOS:
		frappe.throw(_("DDD {0} inválido.").format(ddd), title=_("Telefone inválido"))

	local = numero[2:]

	if phone_type == "mobile":
		if len(numero) != 11:
			frappe.throw(_("Celular deve ter 11 dígitos (DDD + 9 dígitos)."), title=_("Celular inválido"))
		if local[0] != "9":
			frappe.throw(_("Celular deve começar com 9 após o DDD."), title=_("Celular inválido"))
		if local[1] in ("0", "1"):
			frappe.throw(
				_("Segundo dígito do celular não pode ser 0 ou 1."),
				title=_("Celular inválido"),
			)
	else:
		if len(numero) != 10:
			frappe.throw(_("Telefone fixo deve ter 10 dígitos (DDD + 8 dígitos)."), title=_("Telefone inválido"))
		if local[0] not in ("2", "3", "4", "5"):
			frappe.throw(
				_("Telefone fixo: primeiro dígito após o DDD deve ser entre 2 e 5."),
				title=_("Telefone inválido"),
			)

	return numero


def validar_email(email):
	"""Normaliza e-mail (minúsculas); rejeita formato claramente inválido."""
	if not email:
		return email
	email = email.strip().lower()
	if "@" not in email or "." not in email.split("@")[-1]:
		frappe.throw(_("E-mail inválido."), title=_("E-mail inválido"))
	return email
