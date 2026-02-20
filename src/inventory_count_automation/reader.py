"""Leitura e parsing dos arquivos .txt de contagem."""
from pathlib import Path

from inventory_count_automation.settings import LayoutConfig, INPUT_TXT_DIR

def list_txt_files(directory: Path = INPUT_TXT_DIR) -> list[Path]:
    """Retorna todos os arquivos .txt do diretório informado, ordenados por nome."""
    if not directory.exists():
        raise FileNotFoundError(f"Diretório de entrada não encontrado: {directory}")

    files = sorted(directory.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo .txt encontrado em: {directory}")

    return files


def parse_barcodes_from_file(filepath: Path, layout: LayoutConfig) -> list[str]:
    """
    Lê um arquivo .txt e retorna a lista de barcodes válidos.

    Cada linha é tratada (strip) e validada contra o padrão corporativo.
    Linhas vazias ou inválidas são silenciosamente ignoradas.
    """
    barcodes: list[str] = []

    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if raw and layout.compiled_barcode_pattern.match(raw):
                barcodes.append(raw.upper())

    return barcodes


def read_all_barcodes(layout: LayoutConfig, directory: Path = INPUT_TXT_DIR) -> list[str]:
    """
    Varre todos os .txt do diretório e retorna a lista consolidada de barcodes.

    Retorna todos os barcodes (com repetições) para posterior contabilização.
    """
    files = list_txt_files(directory)
    all_barcodes: list[str] = []

    for filepath in files:
        barcodes = parse_barcodes_from_file(filepath, layout)
        print(f"  📄 {filepath.name}: {len(barcodes)} barcodes lidos")
        all_barcodes.extend(barcodes)

    return all_barcodes
