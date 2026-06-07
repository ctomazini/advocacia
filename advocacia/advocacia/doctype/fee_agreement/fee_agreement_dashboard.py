from frappe import _


def get_data():
	return {
		"internal_links": {
			"Legal Case": "legal_case",
		},
		"non_standard_fieldnames": {
			"Legal Payment": "fee_agreement",
		},
	}
