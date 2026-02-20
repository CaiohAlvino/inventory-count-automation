# inventory-count-automation

Sistema desenvolvido em Python para **consolidação de inventário geral** a partir de múltiplos arquivos `.txt`.

O programa lê arquivos de contagem (`.txt`) contendo barcodes, contabiliza o saldo de cada produto e **atualiza automaticamente** uma planilha Excel já pré-preenchida com o cadastro dos produtos, atribuindo a quantidade física (saldo) correspondente a cada item identificado.

Suporta **múltiplos layouts configuráveis** — cada empresa/planilha pode ter seu próprio perfil com colunas, prefixo/sufixo de barcode e nome de arquivo distintos, tudo gerenciado via CLI interativa e persistido em TOML.

---

## Estrutura do Projeto

```
inventory-count-automation/
├── LICENSE
├── pyproject.toml
├── README.md
├── data/
│   ├── config.toml                      # Configuração persistida (layouts, layout ativo)
│   ├── planilhas/
│   │   └── Planilha de Inventário.xlsx   # Planilha pré-preenchida com produtos cadastrados
│   └── txt/
│       ├── contagem_01.txt               # Arquivos de contagem (barcodes)
│       ├── contagem_02.txt
│       └── ...
├── src/
│   └── inventory_count_automation/
│       ├── __init__.py
│       ├── __main__.py                   # Ponto de entrada (CLI)
│       ├── settings.py                   # Dataclasses de configuração, persistência TOML
│       ├── cli.py                        # Setup interativo (CRUD de layouts)
│       ├── reader.py                     # Leitura e parsing dos arquivos .txt
│       ├── counter.py                    # Contabilização e agrupamento dos barcodes
│       └── excel_handler.py              # Identificação dos produtos na planilha e atribuição dos saldos
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
- Filtra os barcodes válidos com base no **prefixo** e/ou **sufixo** configurados no layout ativo (ex.: prefixo `MCS000` aceita apenas códigos que iniciam com `MCS000`).
- Se nenhum prefixo/sufixo estiver configurado, aceita todas as linhas não-vazias.

### 2. Contabilização dos barcodes (`counter.py`)

- Agrupa todos os barcodes extraídos de **todos** os arquivos `.txt`.
- Conta a quantidade de ocorrências (quantidade física) de cada barcode único.
- Gera um dicionário `{barcode: quantidade}` consolidado e ordenado.

### 3. Atribuição de saldos na planilha (`excel_handler.py`)

- Carrega a planilha **pré-preenchida** (definida no layout ativo) que já contém os produtos cadastrados.
- Percorre a coluna configurada como **chave de busca** (`col_chave_busca`), buscando correspondência com cada barcode contabilizado.
- Ao encontrar o barcode, **atribui o saldo** na coluna configurada como **quantidade física** (`col_qtd_fisico`).
- Produtos que existem na planilha mas **não foram contados** permanecem inalterados.
- Barcodes lidos nos `.txt` que **não existem na planilha** são reportados no log como "não encontrados".
- As alterações são salvas diretamente na planilha.

---

## Sistema de Configuração

O projeto utiliza um sistema de configuração em camadas com **múltiplos layouts** para suportar diferentes empresas/planilhas:

### Arquitetura

- **`LayoutConfig`** — dataclass com todas as configurações de um layout: nome do arquivo da planilha, linhas de cabeçalho/dados, colunas primárias e secundárias, prefixo/sufixo de barcode.
- **`AppConfig`** — dataclass que agrupa múltiplos `LayoutConfig` em um dicionário e define qual é o layout ativo.
- **Persistência TOML** — a configuração é salva em `data/config.toml` e carregada automaticamente na execução.

### Campos do Layout

| Campo              | Tipo   | Padrão                                | Descrição                                       |
|--------------------|--------|---------------------------------------|-------------------------------------------------|
| `description`      | `str`  | `""`                                  | Descrição livre do layout                       |
| `planilha_filename`| `str`  | `"Planilha de Inventário Base.xlsx"`  | Nome do arquivo Excel em `data/planilhas/`      |
| `header_row`       | `int`  | `1`                                   | Linha dos cabeçalhos na planilha                |
| `data_start_row`   | `int`  | `2`                                   | Primeira linha de dados                         |
| `col_chave_busca`  | `str`  | `"A"`                                 | Coluna do identificador principal (barcode)     |
| `col_qtd_fisico`   | `str`  | `"Z"`                                 | Coluna onde o saldo físico será escrito         |
| `barcode_prefix`   | `str`  | `""`                                  | Prefixo obrigatório do código (ex: `"MCS000"`)  |
| `barcode_suffix`   | `str`  | `""`                                  | Sufixo obrigatório do código (ex: `"BR"`)       |
| `col_ean`          | `str`  | `""`                                  | Coluna EAN *(opcional)*                         |
| `col_cod_sistema`  | `str`  | `""`                                  | Coluna código do sistema *(opcional)*           |
| `col_cod_xml`      | `str`  | `""`                                  | Coluna código XML *(opcional)*                  |
| `col_descricao`    | `str`  | `""`                                  | Coluna descrição *(opcional)*                   |
| `col_sku`          | `str`  | `""`                                  | Coluna SKU *(opcional)*                         |

### Filtro de Barcode (Prefixo e Sufixo)

O filtro é construído automaticamente a partir dos campos `barcode_prefix` e `barcode_suffix`:

| Prefixo    | Sufixo    | Regex gerada    | Exemplo aceito     |
|------------|-----------|-----------------|--------------------|
| `MCS000`   |           | `^MCS000\S+$`   | `MCS000PROD001`    |
| `MCS000`   | `BR`      | `^MCS000\S+BR$` | `MCS000PROD001BR`  |
|            | `XXX`     | `^\S+XXX$`      | `PROD001XXX`       |
| *(vazio)*  | *(vazio)* | `^.+$`          | *(qualquer linha)* |

---

## Pré-requisitos

- **Python** >= 3.14
- **Poetry** (gerenciador de dependências)

---

## Dependências

| Pacote      | Finalidade                                                 |
|-------------|------------------------------------------------------------|
| `openpyxl`  | Leitura e escrita de arquivos Excel (`.xlsx`)              |
| `tomli-w`   | Escrita de arquivos TOML (leitura via `tomllib` da stdlib) |

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

### 1. Configurar layouts (primeira vez ou quando precisar alterar)

```bash
poetry run inventory-count --setup
```

O menu interativo permite:
- **Adicionar** um novo layout (empresa/planilha)
- **Editar** um layout existente
- **Remover** um layout
- **Selecionar** o layout ativo
- **Salvar e sair** (persiste em `data/config.toml`)

### 2. Preparar os dados de entrada

- Coloque os arquivos `.txt` de contagem em `data/txt/`.
- Certifique-se de que a planilha pré-preenchida está em `data/planilhas/` com o nome configurado no layout ativo.

### 3. Executar o processamento

```bash
poetry run inventory-count
```

O sistema carrega o layout ativo do `config.toml`, lê os `.txt`, contabiliza os barcodes e atualiza a planilha automaticamente.

### 4. Resultado

A planilha configurada no layout ativo será atualizada com os saldos contados na coluna de quantidade física.

---

## Exemplo de `config.toml`

```toml
active_layout = "musical center som"

[layouts.default]
description = "Essa é a configuração base"
planilha_filename = "Planilha de Inventário Base.xlsx"
header_row = 1
data_start_row = 2
col_chave_busca = "A"
col_qtd_fisico = "Z"
col_ean = ""
col_cod_sistema = ""
col_cod_xml = ""
col_descricao = ""
col_sku = ""
barcode_prefix = ""
barcode_suffix = ""

```

---

## Formato dos Arquivos `.txt`

Cada arquivo de contagem deve conter **um barcode por linha**:

```
PRODUTO1
PRODUTO2
PRODUTO1
PRODUTO3
...
```

> Barcodes repetidos são contabilizados (somados) automaticamente como unidades do mesmo produto.

---

## Desenvolvimento

```bash
# Rodar os testes
poetry run pytest

# Rodar com output detalhado
poetry run pytest -v

# Executar o processamento
poetry run inventory-count

# Abrir o setup interativo
poetry run inventory-count --setup
```

---

## Performance

| Cenário                                     | Expectativa          |
|---------------------------------------------|----------------------|
| ~4.000 produtos na planilha                 | ✅ Sem problemas     |
| 10.000+ registros de barcode nos `.txt`     | ✅ Sem problemas     |
| 50.000+ registros (cenário extremo)         | ✅ Funcional (~seg)  |

O `openpyxl` trabalha com a planilha carregada em memória e a busca de barcodes utiliza um **dicionário indexado** (`O(1)` por lookup), de modo que o volume mencionado é processado em **poucos segundos**.

---

## Licença

Este projeto está sob a licença indicada no arquivo [LICENSE](LICENSE).
