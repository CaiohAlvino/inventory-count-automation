"""Testes para o módulo counter."""

from inventory_count_automation.counter import count_barcodes


class TestCountBarcodes:
    def test_counts_correctly(self) -> None:
        barcodes = [
            "MCS000PROD001",
            "MCS000PROD002",
            "MCS000PROD001",
            "MCS000PROD003",
            "MCS000PROD002",
            "MCS000PROD001",
        ]
        result = count_barcodes(barcodes)
        assert result["MCS000PROD001"] == 3
        assert result["MCS000PROD002"] == 2
        assert result["MCS000PROD003"] == 1

    def test_empty_list(self) -> None:
        result = count_barcodes([])
        assert result == {}

    def test_single_item(self) -> None:
        result = count_barcodes(["MCS000ABC"])
        assert result == {"MCS000ABC": 1}

    def test_result_is_sorted(self) -> None:
        barcodes = ["MCS000ZZZ", "MCS000AAA", "MCS000MMM"]
        result = count_barcodes(barcodes)
        keys = list(result.keys())
        assert keys == sorted(keys)
