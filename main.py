import argparse
import csv
from pathlib import Path

from src.normalizer import normalize_row
from src.validator import validate_row
from src.writer import write_csv

VALID_FIELDS = [
    "external_id",
    "name",
    "email",
    "document",
    "phone",
    "zip_code",
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

    write_csv(Path("output/valid.csv"), valid_rows, VALID_FIELDS)
    write_csv(Path("output/invalid.csv"), invalid_rows, INVALID_FIELDS)

    raw_preview_rows = rows[:5]
    normalized_preview_rows = normalized_rows[:5]

    print (f"Encoding utilizado: {encoding}")
    print (f"Total de registos lidos: {len(rows)}")
    print (f"Total de registros normalizados: {len(normalized_rows)}")
    print (f"Total de registros válidos: {len(valid_rows)}")
    print (f"Total de registros inválidos: {len(invalid_rows)}")
    print("Arquivo gerado: output/valid.csv")
    print("Arquivo gerado: output/invalid.csv")

    print ("\nPrévia do dataset original:")

    for row in raw_preview_rows:
        print(row)

    print ("\nPrévia do dataset normalizado:")

    for row in normalized_preview_rows:
        print(row)

    print ("\nRegistros inválidos:")

    for row in invalid_rows:
        print(row)

if __name__ == "__main__":
    main()