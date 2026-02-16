"""Identificação dos produtos na planilha e atribuição dos saldos contados."""

from pathlib import Path

import openpyxl

from inventory_count_automation.config import (
    COL_BARCODE,
    COL_QTD_FISICO,
    DATA_START_ROW,
    INPUT_PLANILHA_DIR,
    OUTPUT_DIR,
    OUTPUT_FILENAME,
    PLANILHA_BASE_FILENAME,
)


def _build_barcode_index(ws, col_barcode: str, start_row: int) -> dict[str, int]:
    """
    Percorre a coluna de barcode da planilha e cria um índice
    {barcode_upper: número_da_linha} para busca O(1).
    """
    index: dict[str, int] = {}

    for row in range(start_row, ws.max_row + 1):
        cell_value = ws[f"{col_barcode}{row}"].value
        if cell_value is not None:
            barcode = str(cell_value).strip().upper()
            if barcode:
                index[barcode] = row

    return index


def load_workbook(filepath: Path | None = None) -> openpyxl.Workbook:
    """Carrega a planilha base do caminho padrão ou de um caminho customizado."""
    if filepath is None:
        filepath = INPUT_PLANILHA_DIR / PLANILHA_BASE_FILENAME

    if not filepath.exists():
        raise FileNotFoundError(f"Planilha base não encontrada: {filepath}")

    return openpyxl.load_workbook(filepath)


def assign_balances(
    counted: dict[str, int],
    wb: openpyxl.Workbook | None = None,
    output_path: Path | None = None,
) -> dict[str, list[str]]:
    """
    Atribui os saldos contados na planilha.

    Parâmetros
    ----------
    counted : dict[str, int]
        Dicionário {barcode: quantidade} gerado pelo counter.
    wb : Workbook, opcional
        Workbook já carregado; se None, carrega do caminho padrão.
    output_path : Path, opcional
        Caminho de saída; se None, usa o padrão.

    Retorna
    -------
    dict com chaves:
        - "matched"     : barcodes encontrados e atualizados
        - "not_found"   : barcodes lidos nos .txt mas ausentes na planilha
    """
    if wb is None:
        wb = load_workbook()

    ws = wb.active
    if ws is None:
        raise ValueError("Workbook não possui uma planilha ativa")

    if output_path is None:
        output_path = OUTPUT_DIR / OUTPUT_FILENAME

    # Garante que o diretório de saída existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Indexa barcode → linha da planilha
    barcode_index = _build_barcode_index(ws, COL_BARCODE, DATA_START_ROW)

    matched: list[str] = []
    not_found: list[str] = []

    for barcode, qty in counted.items():
        row = barcode_index.get(barcode)
        if row is not None:
            ws[f"{COL_QTD_FISICO}{row}"] = qty
            matched.append(barcode)
        else:
            not_found.append(barcode)

    wb.save(output_path)

    # ── Log de resultado ────────────────────────────────────────────────
    print(f"  ✅ Produtos atualizados na planilha: {len(matched)}")

    if not_found:
        print(f"  ⚠️  Barcodes NÃO encontrados na planilha: {len(not_found)}")
        for bc in not_found:
            print(f"      • {bc}")

    print(f"  💾 Arquivo salvo em: {output_path}")

    return {"matched": matched, "not_found": not_found}
