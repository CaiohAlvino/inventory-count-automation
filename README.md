# inventory-count-automation

Sistema desenvolvido em Python para **consolidação de inventário geral** a partir de múltiplos arquivos `.txt`.

O programa lê arquivos de contagem (`.txt`) contendo barcodes no padrão da empresa (`MCS000EXEMPLO`), contabiliza o saldo de cada produto e **atualiza automaticamente** uma planilha Excel já pré-preenchida com o cadastro dos produtos, atribuindo a quantidade física (saldo) correspondente a cada item identificado.

---

## Estrutura do Projeto

```
inventory-count-automation/
├── LICENSE
├── pyproject.toml
├── README.md
├── data/
│   ├── planilha/
│   │   └── modelo_base.xlsx            # Planilha pré-preenchida com ~4000 produtos cadastrados
│   └── txt/
│       ├── contagem_01.txt              # Arquivos de contagem (barcodes)
│       ├── contagem_02.txt
│       └── ...
├── src/
│   └── inventory_count_automation/
│       ├── __init__.py
│       ├── __main__.py                  # Ponto de entrada (CLI)
│       ├── config.py                    # Constantes e configurações (paths, regex, etc.)
│       ├── reader.py                    # Leitura e parsing dos arquivos .txt
│       ├── counter.py                   # Contabilização e agrupamento dos barcodes
│       └── excel_handler.py             # Identificação dos produtos na planilha e atribuição dos saldos
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

- Varre o diretório `data/txt/` e coleta todos os arquivos `.txt`.
- Cada arquivo contém uma lista de barcodes (um por linha), representando itens lidos via coletor ou scanner.
- Filtra apenas os barcodes que seguem o padrão da empresa: **`MCS000XXXXXXX`** (validação via regex).

### 2. Contabilização dos barcodes (`counter.py`)

- Agrupa todos os barcodes extraídos de **todos** os arquivos `.txt`.
- Conta a quantidade de ocorrências (quantidade física) de cada barcode único.
- Gera um dicionário `{barcode: quantidade}` consolidado.

### 3. Atribuição de saldos na planilha (`excel_handler.py`)

- Carrega a planilha **pré-preenchida** (`data/planilha/modelo_base.xlsx`) que já contém **~4.000 produtos cadastrados** com todas as suas características. Estrutura de colunas (a partir da linha 2):

| Coluna | Campo         | Descrição                              | Ação do sistema        |
|--------|---------------|----------------------------------------|------------------------|
| B      | Empresa       | Identificador da empresa               | —                      |
| C      | SKU           | Código interno do produto              | —                      |
| D      | Descrição     | Nome/descrição do produto              | —                      |
| E      | Posição       | Localização no estoque                 | —                      |
| F      | Depósito      | Depósito de armazenagem                | —                      |
| G      | Barcode       | Código de barras (`MCS000...`)         | **Chave de busca** 🔍  |
| H      | Volume/Série  | Volume ou número de série              | —                      |
| I      | Nº NF         | Número da nota fiscal                  | —                      |
| J      | Data          | Data de entrada                        | —                      |
| K      | Lote          | Lote do produto                        | —                      |
| L      | Centro Custo  | Centro de custo associado              | —                      |
| M      | QTD Físico    | Quantidade contada fisicamente         | **Saldo atribuído** ✏️ |
| N      | QTD ALT       | Quantidade alterada                    | —                      |
| O      | Disponível    | Quantidade disponível                  | —                      |

- O sistema **percorre** a coluna **G (Barcode)** da planilha, buscando correspondência com cada barcode contabilizado.
- Ao encontrar o barcode, **atribui o saldo** (quantidade contada) na coluna **M (QTD Físico)** da mesma linha.
- Produtos que existem na planilha mas **não foram contados** permanecem inalterados.
- Barcodes lidos nos `.txt` que **não existem na planilha** são reportados no log como "não encontrados".
- As alterações são salvas **diretamente na planilha original** (`modelo_base.xlsx`).

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

- Coloque os arquivos `.txt` de contagem em `data/txt/`.
- Certifique-se de que a planilha **pré-preenchida** (com todos os produtos cadastrados) está em `data/planilha/modelo_base.xlsx`.

### 2. Executar o sistema

```bash
poetry run python -m inventory_count_automation
```

### 3. Resultado

A planilha original em `data/planilha/modelo_base.xlsx` será atualizada com os saldos contados.

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

## Performance

| Cenário                                      | Expectativa         |
|----------------------------------------------|---------------------|
| ~4.000 produtos na planilha                   | ✅ Sem problemas     |
| 10.000+ registros de barcode nos `.txt`       | ✅ Sem problemas     |
| 50.000+ registros (cenário extremo)           | ✅ Funcional (~seg)  |

O `openpyxl` trabalha com a planilha carregada em memória e a busca de barcodes utiliza um **dicionário indexado** (`O(1)` por lookup), de modo que o volume mencionado é processado em **poucos segundos**.

---

## Licença

Este projeto está sob a licença indicada no arquivo [LICENSE](LICENSE).
