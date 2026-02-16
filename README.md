# inventory-count-automation

Sistema desenvolvido em Python para **consolidação de inventário geral** a partir de múltiplos arquivos `.txt`.

O programa lê arquivos de contagem (`.txt`) contendo barcodes no padrão da empresa (`MCS000EXEMPLO`), contabiliza a quantidade de cada produto e preenche automaticamente uma planilha Excel com os dados consolidados e as características correspondentes de cada item.

---

## Estrutura do Projeto

```
inventory-count-automation/
├── LICENSE
├── pyproject.toml
├── README.md
├── data/
│   ├── input/
│   │   ├── planilha_base/
│   │   │   └── modelo_base.xlsx        # Planilha modelo com cabeçalhos e formatação
│   │   └── txt/
│   │       ├── contagem_01.txt          # Arquivos de contagem (barcodes)
│   │       ├── contagem_02.txt
│   │       └── ...
│   └── output/
│       └── inventario_consolidado.xlsx  # Resultado final gerado pelo sistema
├── src/
│   └── inventory_count_automation/
│       ├── __init__.py
│       ├── __main__.py                  # Ponto de entrada (CLI)
│       ├── config.py                    # Constantes e configurações (paths, regex, etc.)
│       ├── reader.py                    # Leitura e parsing dos arquivos .txt
│       ├── counter.py                   # Contabilização e agrupamento dos barcodes
│       └── excel_handler.py             # Leitura da planilha base e escrita do output
└── tests/
    ├── __init__.py
    ├── test_reader.py
    ├── test_counter.py
    └── test_excel_handler.py
```

---

## Funcionamento

O sistema opera em **3 etapas principais**:

### 1. Leitura dos arquivos `.txt` (`reader.py`)

- Varre o diretório `data/input/txt/` e coleta todos os arquivos `.txt`.
- Cada arquivo contém uma lista de barcodes (um por linha), representando itens lidos via coletor ou scanner.
- Filtra apenas os barcodes que seguem o padrão da empresa: **`MCS000XXXXXXX`** (validação via regex).

### 2. Contabilização dos barcodes (`counter.py`)

- Agrupa todos os barcodes extraídos de **todos** os arquivos `.txt`.
- Conta a quantidade de ocorrências (quantidade física) de cada barcode único.
- Gera um dicionário `{barcode: quantidade}` consolidado.

### 3. Geração da planilha de saída (`excel_handler.py`)

- Carrega a planilha modelo (`data/input/planilha_base/modelo_base.xlsx`) que possui a seguinte estrutura de colunas (a partir da linha 2):

| Coluna | Campo         | Descrição                              |
|--------|---------------|----------------------------------------|
| B      | Empresa       | Identificador da empresa               |
| C      | SKU           | Código interno do produto              |
| D      | Descrição     | Nome/descrição do produto              |
| E      | Posição       | Localização no estoque                 |
| F      | Depósito      | Depósito de armazenagem                |
| G      | Barcode       | Código de barras (`MCS000...`)         |
| H      | Volume/Série  | Volume ou número de série              |
| I      | Nº NF         | Número da nota fiscal                  |
| J      | Data          | Data de entrada                        |
| K      | Lote          | Lote do produto                        |
| L      | Centro Custo  | Centro de custo associado              |
| M      | QTD Físico    | Quantidade contada fisicamente         |
| N      | QTD ALT       | Quantidade alterada                    |
| O      | Disponível    | Quantidade disponível                  |

- Para cada barcode contabilizado, uma linha é preenchida na planilha com o barcode na coluna **G** e a quantidade física na coluna **M**.
- O arquivo final é salvo em `data/output/inventario_consolidado.xlsx`.

---

## Pré-requisitos

- **Python** >= 3.14
- **Poetry** (gerenciador de dependências)

---

## Dependências

| Pacote     | Finalidade                                      |
|------------|--------------------------------------------------|
| `openpyxl` | Leitura e escrita de arquivos Excel (`.xlsx`)    |

> Todas as dependências são gerenciadas via Poetry e declaradas no `pyproject.toml`.

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/CaiohAlvino/inventory-count-automation.git
cd inventory-count-automation

# 2. Instale as dependências com Poetry
poetry install
```

---

## Como Usar

### 1. Preparar os dados de entrada

- Coloque os arquivos `.txt` de contagem em `data/input/txt/`.
- Certifique-se de que a planilha modelo está em `data/input/planilha_base/modelo_base.xlsx`.

### 2. Executar o sistema

```bash
poetry run python -m inventory_count_automation
```

### 3. Resultado

O arquivo consolidado será gerado em:

```
data/output/inventario_consolidado.xlsx
```

---

## Formato dos Arquivos `.txt`

Cada arquivo de contagem deve conter **um barcode por linha**, seguindo o padrão da empresa:

```
MCS000PRODUTO1
MCS000PRODUTO2
MCS000PRODUTO1
MCS000PRODUTO3
...
```

> Barcodes repetidos são contabilizados (somados) automaticamente como unidades do mesmo produto.

---

## Padrão de Barcode

O barcode segue o formato corporativo:

```
MCS000XXXXXXX
```

Onde:
- `MCS` — prefixo fixo da empresa
- `000` — segmento numérico fixo
- `XXXXXXX` — identificador único do produto

---

## Desenvolvimento

```bash
# Rodar os testes
poetry run pytest

# Executar em modo desenvolvimento
poetry run python -m inventory_count_automation
```

---

## Licença

Este projeto está sob a licença indicada no arquivo [LICENSE](LICENSE).
