import json

def build_report(
        total_processed,
        total_valid,
        total_invalid,
        total_created,
        total_updated,
        total_api_failures,
        execution_time,
):
    return {
        "total_processados": total_processed,
        "total_validos": total_valid,
        "total_invalidos": total_invalid,
        "total_criados": total_created,
        "total_atualizados": total_updated,
        "total_falhas_api": total_api_failures,
        "tempo_execucao": execution_time,
    }

def write_report(file_path, report):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open(mode="w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)