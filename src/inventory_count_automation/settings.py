import dataclasses
import re
from pathlib import Path

# ── Diretórios (infraestrutura) ─────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
INPUT_TXT_DIR = DATA_DIR / "txt"
INPUT_PLANILHA_DIR = DATA_DIR / "planilha"

@dataclasses.dataclass
class LayoutConfig:
    """Configurações e constantes do projeto."""

    # ── Metadados ─────────────────────────────────────────────────────────────
    description: str = ""        # Descrição do item

    # ── Planilha ──────────────────────────────────────────────────────────────
    planilha_filename: str = "Planilha de Inventário_Musical Center.xlsx"

    header_row: int = 2          # Linha dos cabeçalhos
    data_start_row: int = 3      # Primeira linha de dados

    # ── Colunas primárias ─────────────────────────────────────────────────────
    col_chave_busca: str = "G"   # Coluna com o identificador principal (SKU, EAN, etc.)
    col_qtd_fisico: str = "M"    # Coluna onde o saldo será atribuído

    # ── Colunas secundárias ───────────────────────────────────────────────────
    col_ean: str = ""            # Coluna com o código EAN
    col_cod_sistema: str = ""    # Coluna com o código do sistema
    col_cod_xml: str = ""        # Coluna com o código do XML
    col_descricao: str = ""      # Coluna com a descrição do item
    col_sku: str = ""            # Coluna com o SKU do item

    # ── Barcode pattern and configuration ─────────────────────────────────────
    barcode_pattern: str = ""    # Exemplo: MCS00012345, MCS000EXEMPLO, etc.

    @property
    def compiled_barcode_pattern(self) -> re.Pattern[str]:
        if not self.barcode_pattern:
            return re.compile(r"^.+$")  # aceita qualquer linha não-vazia
        return re.compile(self.barcode_pattern, re.IGNORECASE)

    def __post_init__(self) -> None:
        # Aqui dentro, faça as validações:
        # 1. header_row >= 1 (senão ValueError)
        # 2. data_start_row > header_row (senão ValueError)
        # 3. col_chave_busca não pode ser vazio (senão ValueError)
        # 4. col_qtd_fisico não pode ser vazio (senão ValueError)
        # 5. tente re.compile(self.barcode_pattern) — se der re.error, lance ValueError com mensagem clara
        if self.header_row < 1:
            raise ValueError(f"header_row (Linha onde os cabeçalhos estão) deve ser maior ou igual a 1.")

        if self.data_start_row <= self.header_row:
            raise ValueError(f"data_start_row (linha onde os dados começam) deve ser maior que header_row (linha dos cabeçalhos).")

        if not self.col_chave_busca:
            raise ValueError("col_chave_busca (coluna onde o barcode está) não pode ser vazio.")

        if not self.col_qtd_fisico:
            raise ValueError("col_qtd_fisico (coluna onde o saldo físico será atribuído) não pode ser vazio.")

        if self.barcode_pattern:
            try:
                re.compile(self.barcode_pattern)
            except re.error as e:
                raise ValueError(f"barcode_pattern é inválido: {e}") from e

@dataclasses.dataclass
class AppConfig:
    """ Configurações globais do aplicativo, incluindo múltiplos layouts de planilha. """

    # ── Configurações gerais ─────────────────────────────────────────────────────
    active_layout: str = "default" # Nome do layout ativo, deve corresponder a uma chave em 'layouts'

    # ── Layouts de planilha ─────────────────────────────────────────────────────
    # Permite definir múltiplos layouts para diferentes formatos de planilha, cada um com suas próprias configurações.
    layouts: dict[str, LayoutConfig] = dataclasses.field(
        default_factory=lambda: {
            "default": LayoutConfig()
        }
    )

    # O layout ativo é acessível via propriedade para uso em todo o aplicativo, garantindo que todas as operações usem as configurações corretas.
    @property
    def active(self) -> LayoutConfig:
        """Retorna o layout ativo."""
        try:
            return self.layouts[self.active_layout]
        except KeyError:
            raise ValueError(
                f"Layout ativo '{self.active_layout}' não encontrado. "
                f"Disponíveis: {list(self.layouts.keys())}"
            ) from None

    def __post_init__(self) -> None:
        # Validações para garantir que o layout ativo exista no dicionário de layouts.

        # Se o layout ativo não for encontrado, lança um ValueError com uma mensagem clara indicando o problema e listando os layouts disponíveis.
        if self.active_layout not in self.layouts:
            raise ValueError(
                f"Layout ativo '{self.active_layout}' não encontrado. "
                f"Disponíveis: {list(self.layouts.keys())}"
            )

    def add_layout(self, name: str, layout_config: LayoutConfig) -> None:
        """ Adiciona um novo layout. Lança ValueError se o nome ja existir."""
        if name in self.layouts:
            raise ValueError(f"Layout '{name}' já existe. Use outro nome ou remova o existente.")
        self.layouts[name] = layout_config

    def remove_layout(self, name: str) -> None:
        """Remove um layout. Não permite remover o layout ativo."""
        if name == self.active_layout:
            raise ValueError(f"Não é possível remover o layout ativo '{name}'. Troque o layout ativo antes.")
        if name not in self.layouts:
            raise KeyError(f"Layout '{name}' não encontrado.")
        del self.layouts[name]

    def set_active(self, name: str) -> None:
        """Define o layout ativo. Lança ValueError se o layout não existir."""
        if name not in self.layouts:
            raise ValueError(
                f"Layout '{name}' não encontrado. "
                f"Disponíveis: {list(self.layouts.keys())}"
            )
        self.active_layout = name
