import re

EXPECTED_FIELDS = [
    "external_id",
    "name",
    "email",
    "document",
    "phone",
    "zip_code",
]

def only_digits(value):
    if not value:
        return ""

    return re.sub(r"\D", "", value)


def normalize_text(value):
    if not value:
        return ""

    return value.strip()

def normalize_email(value):
    return normalize_text(value).lower()

def normalize_row(row):
    return {
        "external_id": normalize_text(row.get("external_id")),
        "name": normalize_text(row.get("name")),
        "email": normalize_email(row.get("email")),
        "document": only_digits(row.get("document")),
        "phone": only_digits(row.get("phone")),
        "zip_code": only_digits(row.get("zip_code")),
    }