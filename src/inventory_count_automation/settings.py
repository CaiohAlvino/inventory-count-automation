from pathlib import Path
import dataclasses
import tomli_w
import tomllib
import re

# ── Diretórios (infraestrutura) ─────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
INPUT_TXT_DIR = DATA_DIR / "txt"
CONFIG_PATH = DATA_DIR / "config.toml"
INPUT_PLANILHA_DIR = DATA_DIR / "planilhas"

@dataclasses.dataclass
class LayoutConfig:
    """Configurações e constantes do projeto."""

    # ── Metadados ─────────────────────────────────────────────────────────────
    description: str = ""        # Descrição do item

    # ── Planilha ──────────────────────────────────────────────────────────────
    planilha_filename: str = "Planilha de Inventário Base.xlsx"

    header_row: int = 1          # Linha dos cabeçalhos
    data_start_row: int = 2      # Primeira linha de dados

    # ── Colunas primárias ─────────────────────────────────────────────────────
    col_chave_busca: str = "A"   # Coluna com o identificador principal (SKU, EAN, etc.)
    col_qtd_fisico: str = "Z"    # Coluna onde o saldo será atribuído

    # ── Colunas secundárias ───────────────────────────────────────────────────
    col_ean: str = ""            # Coluna com o código EAN
    col_cod_sistema: str = ""    # Coluna com o código do sistema
    col_cod_xml: str = ""        # Coluna com o código do XML
    col_descricao: str = ""      # Coluna com a descrição do item
    col_sku: str = ""            # Coluna com o SKU do item

    # ── Barcode — prefixo e sufixo ───────────────────────────────────────────
    barcode_prefix: str = ""    # Prefixo obrigatório do código (ex: "MCS000")
    barcode_suffix: str = ""    # Sufixo obrigatório do código (ex: "BR")

    @property
    def compiled_barcode_pattern(self) -> re.Pattern[str]:
        """ Constrói o regex a partir do prefixo e sufixo informados pelo usuário. """
        if not self.barcode_prefix and not self.barcode_suffix:
            return re.compile(r"^.+$")  # sem filtro — aceita qualquer linha não-vazia

        prefix = re.escape(self.barcode_prefix)
        suffix = re.escape(self.barcode_suffix)

        if prefix and suffix:
            pattern = f"^{prefix}\\S+{suffix}$"
        elif prefix:
            pattern = f"^{prefix}\\S+$"
        else:
            pattern = f"^\\S+{suffix}$"

        return re.compile(pattern, re.IGNORECASE)

    def __post_init__(self) -> None:
        if self.header_row < 1:
            raise ValueError(f"header_row (Linha onde os cabeçalhos estão) deve ser maior ou igual a 1.")

        if self.data_start_row <= self.header_row:
            raise ValueError(f"data_start_row (linha onde os dados começam) deve ser maior que header_row (linha dos cabeçalhos).")

        if not self.col_chave_busca:
            raise ValueError("col_chave_busca (coluna onde o barcode está) não pode ser vazio.")

        if not self.col_qtd_fisico:
            raise ValueError("col_qtd_fisico (coluna onde o saldo físico será atribuído) não pode ser vazio.")

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

def save_config(config: AppConfig, path: Path) -> None:
    """Salva a configuração em um arquivo TOML."""
    with path.open("wb") as f:
        tomli_w.dump(dataclasses.asdict(config), f)

def load_config(path: Path) -> AppConfig:
    """Carrega a configuração de um arquivo TOML."""
    if not path.exists():
        return AppConfig()

    with path.open("rb") as f:
        data = tomllib.load(f)

    # Reconstrói os LayoutConfig a partir dos sub-dicts
    layouts = {}
    for name, layout_data in data.get("layouts", {}).items():
        layouts[name] = LayoutConfig(**layout_data)

    return AppConfig(
        active_layout=data.get("active_layout", "default"),
        layouts=layouts if layouts else {"default": LayoutConfig()}
    )
