"""Testes para o módulo reader."""

import tempfile
from pathlib import Path

import pytest

from inventory_count_automation.settings import LayoutConfig
from inventory_count_automation.reader import (
    list_txt_files,
    parse_barcodes_from_file,
    read_all_barcodes,
)


@pytest.fixture
def layout() -> LayoutConfig:
    return LayoutConfig(barcode_prefix="MCS000")

@pytest.fixture
def tmp_txt_dir(tmp_path: Path) -> Path:
    """Cria um diretório temporário com arquivos .txt de teste."""
    file1 = tmp_path / "contagem_01.txt"
    file1.write_text(
        "MCS000PROD001\n"
        "MCS000PROD002\n"
        "MCS000PROD001\n"
        "linha_invalida\n"
        "\n"
        "MCS000PROD003\n",
        encoding="utf-8",
    )

    file2 = tmp_path / "contagem_02.txt"
    file2.write_text(
        "MCS000PROD002\n"
        "MCS000PROD004\n",
        encoding="utf-8",
    )

    return tmp_path


class TestListTxtFiles:
    def test_returns_sorted_txt_files(self, tmp_txt_dir: Path) -> None:
        files = list_txt_files(tmp_txt_dir)
        assert len(files) == 2
        assert files[0].name == "contagem_01.txt"
        assert files[1].name == "contagem_02.txt"

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            list_txt_files(tmp_path / "nao_existe")

    def test_raises_on_empty_directory(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            list_txt_files(tmp_path / "vazio")


class TestParseBarcodes:
    def test_parses_valid_barcodes(self, tmp_txt_dir: Path, layout: LayoutConfig) -> None:
        barcodes = parse_barcodes_from_file(tmp_txt_dir / "contagem_01.txt", layout)
        assert barcodes == ["MCS000PROD001", "MCS000PROD002", "MCS000PROD001", "MCS000PROD003"]

    def test_ignores_invalid_lines(self, tmp_txt_dir: Path, layout: LayoutConfig) -> None:
        barcodes = parse_barcodes_from_file(tmp_txt_dir / "contagem_01.txt", layout)
        assert "linha_invalida" not in barcodes
        assert "" not in barcodes

    def test_uppercases_barcodes(self, tmp_path: Path, layout: LayoutConfig) -> None:
        f = tmp_path / "lower.txt"
        f.write_text("mcs000produto\n", encoding="utf-8")
        barcodes = parse_barcodes_from_file(f, layout)
        assert barcodes == ["MCS000PRODUTO"]


class TestReadAllBarcodes:
    def test_consolidates_all_files(self, tmp_txt_dir: Path, layout: LayoutConfig) -> None:
        all_barcodes = read_all_barcodes(layout, tmp_txt_dir)
        assert len(all_barcodes) == 6  # 4 do file1 + 2 do file2
        assert all_barcodes.count("MCS000PROD001") == 2
        assert all_barcodes.count("MCS000PROD002") == 2
