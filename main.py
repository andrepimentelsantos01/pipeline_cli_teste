import argparse
import csv
from pathlib import Path

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
    preview_rows = rows[:5]

    print(f"Encoding utilizado: {encoding}")
    print(f"Total de registos lidos: {len(rows)}")

    print("\nPrévia do dataset ingerido:")

    for row in preview_rows:
        print(row)

if __name__ == "__main__":
    main()