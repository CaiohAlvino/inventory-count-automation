from pathlib import Path
import dataclasses

from inventory_count_automation.settings import LayoutConfig, INPUT_TXT_DIR


@dataclasses.dataclass
class ReadResult:
    """Resultado consolidado da leitura de barcodes."""
    barcodes: list[str]
    rejected: list[str]

def list_txt_files(directory: Path = INPUT_TXT_DIR) -> list[Path]:
    """Retorna todos os arquivos .txt do diretório informado, ordenados por nome."""
    if not directory.exists():
        raise FileNotFoundError(f"Diretório de entrada não encontrado: {directory}")

    files = sorted(directory.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo .txt encontrado em: {directory}")

    return files


def parse_barcodes_from_file(filepath: Path, layout: LayoutConfig) -> ReadResult:
    """
    Lê um arquivo .txt e retorna os barcodes válidos e as linhas rejeitadas.

    Cada linha é tratada (strip) e validada contra o padrão corporativo.
    Linhas vazias são ignoradas. Linhas não-vazias que não correspondem
    ao padrão são registradas como rejeitadas.
    """
    barcodes: list[str] = []
    rejected: list[str] = []

    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            if layout.compiled_barcode_pattern.match(raw):
                barcodes.append(raw.upper())
            else:
                rejected.append(raw)

    return ReadResult(barcodes=barcodes, rejected=rejected)


def read_all_barcodes(layout: LayoutConfig, directory: Path = INPUT_TXT_DIR) -> ReadResult:
    """
    Varre todos os .txt do diretório e retorna o resultado consolidado.

    Retorna um ReadResult com todos os barcodes (com repetições) e
    todas as linhas rejeitadas para posterior análise.
    """
    files = list_txt_files(directory)
    all_barcodes: list[str] = []
    all_rejected: list[str] = []

    for filepath in files:
        result = parse_barcodes_from_file(filepath, layout)
        msg = f"  📄 {filepath.name}: {len(result.barcodes)} barcodes lidos"
        if result.rejected:
            msg += f" ({len(result.rejected)} linhas rejeitadas)"
        print(msg)
        all_barcodes.extend(result.barcodes)
        all_rejected.extend(result.rejected)

    return ReadResult(barcodes=all_barcodes, rejected=all_rejected)
