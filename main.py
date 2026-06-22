import argparse
import csv
import time
from pathlib import Path

from src.normalizer import normalize_row
from src.validator import validate_row, deduplicate_valid_rows
from src.writer import write_csv
from src.viacep_client import get_address_by_zip_code
from src.internal_api_client import send_client
from src.report import build_report, write_report

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
    started_at = time.perf_counter()

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

    total_created = 0
    total_updated = 0
    total_internal_api_failures = 0

    for client in enriched_valid_rows:
        result = send_client(client)

        if result == "created":
            total_created += 1
        elif result == "updated":
            total_updated += 1
        else:
            total_internal_api_failures += 1

    execution_time = round(time.perf_counter() - started_at, 2)

    report = build_report(
        total_processed=len(rows),
        total_valid=len(deduplicated_valid_rows),
        total_invalid=len(invalid_rows),
        total_created=total_created,
        total_updated=total_updated,
        total_api_failures=viacep_failures + total_internal_api_failures,
        execution_time=execution_time,
    )

    write_csv(Path("output/valid.csv"), enriched_valid_rows, VALID_FIELDS)
    write_csv(Path("output/invalid.csv"), invalid_rows, INVALID_FIELDS)
    write_report(Path("output/report.json"), report)

    raw_preview_rows = rows[:5]
    normalized_preview_rows = normalized_rows[:5]
    enriched_preview_rows = enriched_valid_rows[:5]

    print (f"Encoding utilizado: {encoding}")
    print (f"Total de registos lidos: {len(rows)}")
    print (f"Total de registros normalizados: {len(normalized_rows)}")
    print (f"Total de registros válidos antes da deduplicação: {len(valid_rows)}")
    print (f"Total de registros válidos após deduplicação: {len(deduplicated_valid_rows)}")
    print (f"Total de external_ids duplicados: {len(duplicated_external_ids)}")
    print (f"Total de registros inválidos: {len(invalid_rows)}")
    print (f"Total de falhas ViaCEP: {viacep_failures}")
    print (f"Total de registros criados na API interna: {total_created}")
    print (f"Total de registros atualizados na API interna: {total_updated}")
    print (f"Total de falhas na API interna: {total_internal_api_failures}")
    print (f"Tempo de execução: {execution_time}s")
    print ("Arquivo gerado: output/valid.csv")
    print ("Arquivo gerado: output/invalid.csv")
    print ("Arquivo gerado: output/report.json")

    print ("\nPrévia do dataset original:")

    for row in raw_preview_rows:
        print(row)

    print ("\nPrévia do dataset normalizado:")

    for row in normalized_preview_rows:
        print(row)

    print ("\nPrévia do dataset válido enriquecido com ViaCEP")

    for row in enriched_preview_rows:
        print(row)

if __name__ == "__main__":
    main()