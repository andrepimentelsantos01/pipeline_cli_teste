from src.normalizer import normalize_row

def test_normalize_row():
    row = {
        "external_id": " 001 ",
        "name": " João Silva ",
        "email": "JOAO@EMAIL.COM",
        "document": "123.456.789-00",
        "phone": "(11) 99999-9999",
        "zip_code": "01001-000",
    }

    result = normalize_row(row)

    assert result == {
        "external_id": "001",
        "name": "João Silva",
        "email": "joao@email.com",
        "document": "12345678900",
        "phone": "11999999999",
        "zip_code": "01001000",
    }