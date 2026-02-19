import dataclasses
import re
from pathlib import Path

@dataclasses.dataclass
class Config:
    """Configurações e constantes do projeto."""

    # ── Diretórios ──────────────────────────────────────────────────────────
    root_dir: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = root_dir / "data"

    input_txt_dir: Path = data_dir / "txt"
    input_planilha_dir: Path = data_dir / "planilha"

    planilha_base_filename: str = "Planilha de Inventário_Musical Center.xlsx"

    # ── Planilha ────────────────────────────────────────────────────────────
    header_row: int = 2          # Linha dos cabeçalhos
    data_start_row: int = 3      # Primeira linha de dados
    col_barcode: str = "G"       # Coluna com o barcode (chave de busca)
    col_qtd_fisico: str = "M"    # Coluna onde o saldo será atribuído

    # ── Colunas primárias ───────────────────────
    # (campos obrigatórios aqui)

    # ── Colunas secundárias ─────────────────────
    # (campos opcionais aqui)

    # ── Barcode pattern ─────────────────────────────────────────────────────────────
    barcode_pattern: re.Pattern = re.compile(r"^MCS\d{3}\S+$", re.IGNORECASE)
