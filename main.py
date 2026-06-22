import argparse
import csv
from pathlib import Path

from src.normalizer import normalize_row
from src.validator import validate_row, deduplicate_valid_rows
from src.writer import write_csv
from src.viacep_client import get_address_by_zip_code

VALID_FIELDS = [
    "external_id",
    "name",
    "email",
    "document",
    "phone",
    "zip_code",
    "street",
    "neighborhood",
    "city",
    "state",
]

INVALID_FIELDS = [
    *VALID_FIELDS,
    "invalid_reason",
]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Pipeline CLI para importação via CSV"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Caminho do CSV de entrada",
    )

    return parser.parse_args()

def read_csv(input_path):
    encodings = ["utf-8-sig", "cp1252"]

    for encoding in encodings:
        try:
            with input_path.open(mode="r", encoding=encoding, newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

                return rows, encoding

        except UnicodeDecodeError:
            continue

    raise ValueError("Não foi possível ler o CSV, encoding não suportado. Revisar a função de fallback do encoding.")

def main():
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    print(f"Arquivo CSV recebido com sucesso: {input_path}")

    rows, encoding = read_csv(input_path)
    normalized_rows = [normalize_row(row) for row in rows]

    valid_rows = []
    invalid_rows = []
    for row in normalized_rows:
        is_valid, reason = validate_row(row)

        if is_valid:
            valid_rows.append(row)
        else:
            invalid_rows.append({
                **row,
                "invalid_reason": reason,
            })

    deduplicated_valid_rows, duplicated_external_ids = deduplicate_valid_rows(valid_rows)

    enriched_valid_rows = []
    viacep_failures = 0

    for row in deduplicated_valid_rows:
        address = get_address_by_zip_code(row.get("zip_code"))

        if address:
            enriched_valid_rows.append({
                **row,
                **address,
            })
        else:
            viacep_failures += 1
            enriched_valid_rows.append({
                **row,
                "street": "",
                "neighborhood": "",
                "city": "",
                "state": "",
            })

    write_csv(Path("output/valid.csv"), enriched_valid_rows, VALID_FIELDS)
    write_csv(Path("output/invalid.csv"), invalid_rows, INVALID_FIELDS)

    raw_preview_rows = rows[:5]
    normalized_preview_rows = normalized_rows[:5]
    enriched_valid_rows = enriched_valid_rows[:5]

    print (f"Encoding utilizado: {encoding}")
    print (f"Total de registos lidos: {len(rows)}")
    print (f"Total de registros normalizados: {len(normalized_rows)}")
    print (f"Total de registros válidos antes da deduplicação: {len(valid_rows)}")
    print (f"Total de registros válidos após deduplicação: {len(deduplicated_valid_rows)}")
    print (f"Total de external_ids duplicados: {len(duplicated_external_ids)}")
    print (f"Total de registros inválidos: {len(invalid_rows)}")
    print (f"Total de falhas ViaCEP: {viacep_failures}")
    print ("Arquivo gerado: output/valid.csv")
    print ("Arquivo gerado: output/invalid.csv")

    print ("\nPrévia do dataset original:")

    for row in raw_preview_rows:
        print(row)

    print ("\nPrévia do dataset normalizado:")

    for row in normalized_preview_rows:
        print(row)

    print ("\nPrévia do dataset válido enriquecido com ViaCEP")

    for row in enriched_valid_rows:
        print(row)

if __name__ == "__main__":
    main()