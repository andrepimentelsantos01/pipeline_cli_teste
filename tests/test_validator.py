from src.validator import validate_row, deduplicate_valid_rows


def test_validate_row_returns_invalid_when_email_is_invalid():
    row = {
        "external_id": "003",
        "name": "Ana",
        "email": "ana.email.com",
        "document": "12345678900",
        "phone": "11988887777",
        "zip_code": "01001000",
    }

    is_valid, reason = validate_row(row)

    assert is_valid is False
    assert reason == "O campo 'EMAIL' é inválido."


def test_validate_row_returns_invalid_when_external_id_is_empty():
    row = {
        "external_id": "",
        "name": "Aline Lima",
        "email": "aline@email.com",
        "document": "12345678900",
        "phone": "11977776666",
        "zip_code": "01001000",
    }

    is_valid, reason = validate_row(row)

    assert is_valid is False
    assert reason == "O campo 'EXTERNAL_ID' é obrigatório"


def test_deduplicate_valid_rows_keeps_last_external_id_occurrence():
    rows = [
        {"external_id": "001", "name": "João Silva"},
        {"external_id": "002", "name": "Maria Souza"},
        {"external_id": "001", "name": "João Silva Atualizado"},
    ]

    deduplicated_rows, duplicated_external_ids = deduplicate_valid_rows(rows)

    assert deduplicated_rows == [
        {"external_id": "001", "name": "João Silva Atualizado"},
        {"external_id": "002", "name": "Maria Souza"},
    ]
    assert duplicated_external_ids == ["001"]