"""Ponto de entrada do sistema de consolidação de inventário."""

import sys

from inventory_count_automation.settings import load_config, CONFIG_PATH
from inventory_count_automation.counter import count_barcodes, summary
from inventory_count_automation.excel_handler import assign_balances
from inventory_count_automation.reader import read_all_barcodes


def main() -> None:
    config = load_config(CONFIG_PATH)
    layout = config.active

    print("=" * 60)
    print("  INVENTORY COUNT AUTOMATION")
    print("  Consolidação de Inventário")
    print("=" * 60)

    # ── Etapa 1: Leitura dos arquivos .txt ──────────────────────────────
    print("\n📂 Etapa 1 — Leitura dos arquivos .txt")
    try:
        all_barcodes = read_all_barcodes(layout)
    except FileNotFoundError as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

    if not all_barcodes:
        print("\n⚠️  Nenhum barcode válido encontrado nos arquivos. Encerrando.")
        sys.exit(0)

    # ── Etapa 2: Contabilização ─────────────────────────────────────────
    print("\n🔄 Etapa 2 — Contabilização dos barcodes")
    counted = count_barcodes(all_barcodes)
    summary(counted)

    # ── Etapa 3: Atribuição na planilha ─────────────────────────────────
    print("\n📊 Etapa 3 — Atribuição de saldos na planilha")
    try:
        result = assign_balances(layout, counted)
    except FileNotFoundError as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

    # ── Resumo final ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ Processo concluído com sucesso!")
    if result["not_found"]:
        print(f"  ⚠️  {len(result['not_found'])} barcode(s) não encontrado(s)")
    print("=" * 60)


if __name__ == "__main__":
    main()
