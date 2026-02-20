from collections import Counter


def count_barcodes(barcodes: list[str]) -> dict[str, int]:
    """
    Recebe uma lista de barcodes (com repetições) e retorna um dicionário
    {barcode: quantidade} ordenado por barcode.
    """
    counter = Counter(barcodes)
    return dict(sorted(counter.items()))


def summary(counted: dict[str, int]) -> None:
    """Imprime um resumo da contagem no console."""
    total_unique = len(counted)
    total_units = sum(counted.values())
    print(f"  🔢 Produtos únicos identificados: {total_unique}")
    print(f"  📦 Total de unidades contabilizadas: {total_units}")
