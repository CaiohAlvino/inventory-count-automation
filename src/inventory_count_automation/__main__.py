import sys

from inventory_count_automation.settings import load_config, CONFIG_PATH
from inventory_count_automation.counter import count_barcodes, summary
from inventory_count_automation.excel_handler import assign_balances
from inventory_count_automation.reader import read_all_barcodes, ReadResult
from inventory_count_automation.cli import run_setup


def _print_unmatched_report(
    read_result: ReadResult,
    not_found: list[str],
    counted: dict[str, int],
) -> None:
    """
    Exibe o relatório detalhado dos códigos não identificados.

    Inclui:
    - Linhas rejeitadas na leitura (não correspondem ao padrão de barcode)
    - Barcodes lidos nos .txt mas não encontrados na planilha
    """
    has_issues = bool(read_result.rejected) or bool(not_found)

    if not has_issues:
        print("\n  ✅ Todos os códigos foram identificados e atribuídos com sucesso!")
        return

    print("\n" + "=" * 60)
    print("  📋 RELATÓRIO DE CÓDIGOS NÃO IDENTIFICADOS")
    print("=" * 60)

    if read_result.rejected:
        unique_rejected = sorted(set(read_result.rejected))
        print(
            f"\n  ❌ Linhas rejeitadas na leitura "
            f"({len(read_result.rejected)} ocorrências, "
            f"{len(unique_rejected)} únicas):"
        )
        print("     Não correspondem ao padrão de barcode configurado.\n")
        for line in unique_rejected:
            print(f"     • {line}")

    if not_found:
        print(
            f"\n  ⚠️  Barcodes não encontrados na planilha "
            f"({len(not_found)} códigos):"
        )
        print("     Lidos nos .txt, mas sem correspondência na planilha.\n")
        for barcode in sorted(not_found):
            qty = counted.get(barcode, 0)
            print(f"     • {barcode}  (qtd lida: {qty})")

    print()


def main() -> None:
    # Se pediu setup, executa e sai
    if "--setup" in sys.argv:
        run_setup()
        return

    # Caso contrário, executa o processamento normal
    config = load_config(CONFIG_PATH)
    layout = config.active

    print("=" * 60)
    print("  INVENTORY COUNT AUTOMATION")
    print("  Consolidação de Inventário")
    print("=" * 60)

    # ── Etapa 1: Leitura dos arquivos .txt ──────────────────────────────
    print("\n📂 Etapa 1 — Leitura dos arquivos .txt")
    try:
        read_result = read_all_barcodes(layout)
    except FileNotFoundError as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

    if not read_result.barcodes:
        print("\n⚠️  Nenhum barcode válido encontrado nos arquivos. Encerrando.")
        sys.exit(0)

    # ── Etapa 2: Contabilização ─────────────────────────────────────────
    print("\n🔄 Etapa 2 — Contabilização dos barcodes")
    counted = count_barcodes(read_result.barcodes)
    summary(counted)

    # ── Etapa 3: Atribuição na planilha ─────────────────────────────────
    print("\n📊 Etapa 3 — Atribuição de saldos na planilha")
    try:
        result = assign_balances(layout, counted)
    except FileNotFoundError as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

    # ── Resumo final ────────────────────────────────────────────────────
    # ── Etapa 4: Relatório de códigos não identificados ──────────
    _print_unmatched_report(read_result, result["not_found"], counted)

    print("=" * 60)
    print("  ✅ Processo concluído com sucesso!")
    if result["not_found"] or read_result.rejected:
        total = len(result["not_found"]) + len(set(read_result.rejected))
        print(f"  ⚠️  {total} código(s) não identificado(s) — veja o relatório acima")
    print("=" * 60)


if __name__ == "__main__":
    main()
