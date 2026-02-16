"""Configurações e constantes do projeto."""

import re
from pathlib import Path

# ── Diretórios ──────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"

INPUT_TXT_DIR = DATA_DIR / "txt"
INPUT_PLANILHA_DIR = DATA_DIR / "planilha"

PLANILHA_BASE_FILENAME = "modelo_base.xlsx"

# ── Planilha ────────────────────────────────────────────────────────────
HEADER_ROW = 2          # Linha dos cabeçalhos
DATA_START_ROW = 3      # Primeira linha de dados
COL_BARCODE = "G"       # Coluna com o barcode (chave de busca)
COL_QTD_FISICO = "M"    # Coluna onde o saldo será atribuído

# ── Barcode ─────────────────────────────────────────────────────────────
BARCODE_PATTERN = re.compile(r"^MCS\d{3}\S+$", re.IGNORECASE)
