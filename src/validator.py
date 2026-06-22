import re

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

def is_valid_email(email):
    return re.match(EMAIL_PATTERN, email) is not None

def validate_row(row):
    if not row.get("external_id"):
        return False, "O campo 'EXTERNAL_ID' é obrigatório"

    name = row.get("name", "")
    if len(name) < 2:
        return False, "O campo 'NAME' deve ter no mínimo 2 caracteres."

    email = row.get("email", "")
    if email and not is_valid_email(email):
        return False, "O campo 'EMAIL' é inválido."

    document = row.get("document", "")
    if document and len(document) not in (11, 14):
        return False, "O campo 'DOCUMENT' deve ter entre 11 ou 14 dígitos (CPF ou CNPJ)."

    phone = row.get ("phone", "")
    if phone and not phone.isdigit():
        return False, "O campo 'PHONE' deve conter apenas números."

    zip_code = row.get("zip_code", "")
    if zip_code and (not zip_code.isdigit() or len(zip_code) != 8):
        return False, "O campo 'ZIP_CODE' deve conter apenas 8 dígitos numéricos."

    return True, ""

def deduplicate_valid_rows(rows):
    deduplicated_rows_by_external_id = {}
    duplicated_external_ids = []

    for row in rows:
        external_id = row["external_id"]

        if external_id in deduplicated_rows_by_external_id:
            duplicated_external_ids.append(external_id)

        deduplicated_rows_by_external_id[external_id] = row

    return list(deduplicated_rows_by_external_id.values()), duplicated_external_ids