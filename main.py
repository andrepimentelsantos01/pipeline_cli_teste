import argparse
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

def main():
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    print(f"Arquivo CSV recebido com sucesso: {input_path}")

if __name__ == "__main__":
    main()