from inventory_count_automation.settings import (
    LayoutConfig,
    AppConfig,
    save_config,
    load_config,
    CONFIG_PATH
)

def run_setup():
    config = load_config(CONFIG_PATH)

    while True:
        _show_menu(config)
        choice = input("\nEscolha uma opção: ").strip().upper()

        if choice == "A":
            _add_layout(config)
        elif choice == "E":
            _edit_layout(config)
        elif choice == "R":
            _remove_layout(config)
        elif choice == "S":
            _select_active(config)
        elif choice == "Q":
            save_config(config, CONFIG_PATH)
            print("✅ Configuração salva com sucesso!")
            break
        else:
            print("❌ Opção inválida.")

def _show_menu(config: AppConfig) -> None:
    """Exibe o menu principal do setup."""
    print("\n" + "=" * 50)
    print("  CONFIGURAÇÃO DE LAYOUTS")
    print("=" * 50)

    if config.layouts:
        print("\nLayouts disponíveis:")
        # enumerate(iterable, start) → gera (1, item), (2, item), ...
        for i, (name, layout) in enumerate(config.layouts.items(), 1):
            # Marca o layout ativo com ✓
            marker = " (ativo) ✓" if name == config.active_layout else ""
            # Mostra descrição se tiver
            desc = f" — {layout.description}" if layout.description else ""
            print(f"  {i}. {name}{marker}{desc}")
    else:
        print("Nenhum layout disponível.")

    print()
    print("  [A] Adicionar layout")
    print("  [E] Editar layout existente")
    print("  [R] Remover layout")
    print("  [S] Selecionar layout ativo")
    print("  [Q] Salvar e sair")

def _prompt_layout_fields(base: LayoutConfig | None = None) -> LayoutConfig:
    """Coleta os dados de um layout via input interativo."""
    # Se não tem base, usa defaults
    if base is None:
        base = LayoutConfig()

    print("\n Preencha os campos (Enter = manter valor atual):\n")

    # ── Campos de texto: padrão simples ──────────────────
    # O truque: input(...) or default
    # Se o usuário digitar algo → usa o que digitou
    # Se apertar Enter (string vazia) → string vazia é falsy → usa default
    description = input(f"  Descrição [{base.description or 'sem descrição'}]: ").strip() or base.description

    print("\n Agora vamos configurar a planilha\n")
    planilha_filename = input(f"  Nome do arquivo de planilha [{base.planilha_filename or 'sem nome'}]: ").strip() or base.planilha_filename

    # ── Campos numéricos: precisa converter ──────────────
    # Aqui o truque é diferente porque int() não aceita string vazia
    header_row_input = input(f"  Linha do cabeçalho [{base.header_row}]: ").strip()
    # Se digitou algo, converte. Se vazio, mantém o default.
    header_row = int(header_row_input) if header_row_input else base.header_row

    data_start_row_input = input(f"  Primeira linha de dados [{base.data_start_row}]: ").strip()
    data_start_row = int(data_start_row_input) if data_start_row_input else base.data_start_row

    # ── Colunas primárias ────────────────────────────────
    col_chave_busca = input(f"  Coluna da chave de busca (*Onde terá o código que será buscado para identificar o item*) [{base.col_chave_busca}]: ").strip().upper() or base.col_chave_busca

    col_qtd_fisico = input(f"  Coluna do saldo físico [{base.col_qtd_fisico}]: ").strip().upper() or base.col_qtd_fisico

    # ── Barcode — prefixo e sufixo ───────────────────────
    print(f"\n  Prefixo e sufixo do código de barras (vazio = sem filtro)")
    barcode_prefix = input(f"  Prefixo [{base.barcode_prefix or 'nenhum'}]: ").strip()
    if not barcode_prefix:
        barcode_prefix = base.barcode_prefix

    barcode_suffix = input(f"  Sufixo [{base.barcode_suffix or 'nenhum'}]: ").strip()
    if not barcode_suffix:
        barcode_suffix = base.barcode_suffix

    # ── Colunas secundárias (opcionais) ──────────────────
    configurar_secundarias = input("\n  Configurar colunas secundárias? [s/N]: ").strip().lower()

    if configurar_secundarias == "s":
        col_ean = input(f"  Coluna EAN [{base.col_ean or 'vazio'}]: ").strip().upper() or base.col_ean
        col_cod_sistema = input(f"  Coluna código sistema [{base.col_cod_sistema or 'vazio'}]: ").strip().upper() or base.col_cod_sistema
        col_cod_xml = input(f"  Coluna código XML [{base.col_cod_xml or 'vazio'}]: ").strip().upper() or base.col_cod_xml
        col_descricao = input(f"  Coluna descrição [{base.col_descricao or 'vazio'}]: ").strip().upper() or base.col_descricao
        col_sku = input(f"  Coluna SKU [{base.col_sku or 'vazio'}]: ").strip().upper() or base.col_sku
    else:
        # Mantém os valores que já tinha
        col_ean = base.col_ean
        col_cod_sistema = base.col_cod_sistema
        col_cod_xml = base.col_cod_xml
        col_descricao = base.col_descricao
        col_sku = base.col_sku

    # ── Cria e retorna o LayoutConfig ────────────────────
    # Se os dados forem inválidos, o __post_init__ vai lançar ValueError
    return LayoutConfig(
        description=description,
        planilha_filename=planilha_filename,
        header_row=header_row,
        data_start_row=data_start_row,
        col_chave_busca=col_chave_busca,
        col_qtd_fisico=col_qtd_fisico,
        col_ean=col_ean,
        col_cod_sistema=col_cod_sistema,
        col_cod_xml=col_cod_xml,
        col_descricao=col_descricao,
        col_sku=col_sku,
        barcode_prefix=barcode_prefix,
        barcode_suffix=barcode_suffix,
    )

def _add_layout(config: AppConfig) -> None:
    """Adiciona um novo layout via input interativo."""
    name = input("\n  Nome do novo layout: ").strip().lower()
    if not name:
        print("  ❌ Nome não pode ser vazio.")
        return

    try:
        layout = _prompt_layout_fields()  # sem base = defaults
        config.add_layout(name, layout)
        print(f"\n  ✅ Layout '{name}' adicionado com sucesso!")
    except ValueError as e:
        print(f"\n  ❌ Erro: {e}")

def _edit_layout(config: AppConfig) -> None:
    """Edita um layout existente."""
    name = _choose_layout(config, "editar")
    if name is None:
        return

    try:
        # Passa o layout atual como base → defaults mostram valores atuais
        layout = _prompt_layout_fields(base=config.layouts[name])
        config.layouts[name] = layout
        print(f"\n  ✅ Layout '{name}' atualizado com sucesso!")
    except ValueError as e:
        print(f"\n  ❌ Erro: {e}")

def _remove_layout(config: AppConfig) -> None:
    """Remove um layout existente."""
    name = _choose_layout(config, "remover")
    if name is None:
        return

    try:
        config.remove_layout(name)
        print(f"\n  ✅ Layout '{name}' removido!")
    except (ValueError, KeyError) as e:
        print(f"\n  ❌ Erro: {e}")

def _select_active(config: AppConfig) -> None:
    """Seleciona o layout ativo."""
    name = _choose_layout(config, "ativar")
    if name is None:
        return

    try:
        config.set_active(name)
        print(f"\n  ✅ Layout ativo: '{name}'")
    except ValueError as e:
        print(f"\n  ❌ Erro: {e}")

def _choose_layout(config: AppConfig, action: str) -> str | None:
    """Mostra layouts numerados e retorna o nome do escolhido (ou None)."""
    names = list(config.layouts.keys())

    print(f"\n  Qual layout deseja {action}?")
    for i, name in enumerate(names, 1):
        marker = " (ativo)" if name == config.active_layout else ""
        print(f"    {i}. {name}{marker}")

    choice = input("\n  Número (ou Enter para cancelar): ").strip()
    if not choice:
        return None

    try:
        index = int(choice) - 1  # converte para índice 0-based
        return names[index]
    except (ValueError, IndexError):
        print("  ❌ Opção inválida.")
        return None
