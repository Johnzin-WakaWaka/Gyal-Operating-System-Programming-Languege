import sys

def compilar_gyal(arquivo_entrada, arquivo_saida):
    print(f"Lendo código fonte: {arquivo_entrada}...")
    
    try:
        with open(arquivo_entrada, 'r') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo_entrada} não encontrado!")
        return

    # Cabeçalho do Bootloader (Modo Real 16-bits)
    codigo_asm = [
        "; --- GYAL OS COMPILER v0.0.0.1 ---",
        "bits 16",
        "org 0x7C00",
        "jmp _gyal_start",
        "",
        "_gyal_start:",
        "    mov ax, 0",
        "    mov ds, ax",
        "    mov es, ax"
    ]

    secao_dados = []
    variaveis_alocadas = []
    contador_strings = 0
    contador_ifs = 0
    pilha_blocos = [] # Controla a indentação do Python (if/elif/else)

    for linha_num, linha_original in enumerate(linhas):
        # Calcula quantos espaços tem no começo da linha (indentação)
        indentacao = len(linha_original) - len(linha_original.lstrip())
        linha = linha_original.strip()
        
        if not linha or linha.startswith("#"): 
            continue

        # Fecha blocos (if/elif/else) se a indentação voltar ao normal
        while pilha_blocos:
            bloco_atual = pilha_blocos[-1]
            
            # Se a linha atual estiver mais pra frente, continua dentro do bloco
            if indentacao > bloco_atual['indent']:
                break
                
            # Se a linha atual for um elif ou else do MESMO bloco, não fecha ainda
            if indentacao == bloco_atual['indent'] and (linha.startswith("elif ") or linha.startswith("else:")):
                break
            
            # Se chegou aqui, o bloco acabou! Vamos colocar as etiquetas de saída
            bloco = pilha_blocos.pop()
            if bloco['id_cond'] is not None:
                codigo_asm.append(f"__end_cond_{bloco['id_cond']}:")
            codigo_asm.append(f"__end_chain_{bloco['id_chain']}:")

        # Comando: print "texto"
        if linha.startswith("print "):
            inicio = linha.find('"') + 1
            fim = linha.rfind('"')
            if inicio > 0 and fim > inicio:
                texto = linha[inicio:fim]
                nome_string = f"str_{contador_strings}"
                contador_strings += 1
                secao_dados.append(f'{nome_string} db "{texto}", 13, 10, 0')
                codigo_asm.append(f"    mov si, {nome_string}")
                codigo_asm.append("    call _sys_print")

        # Comando: input variavel
        elif linha.startswith("input "):
            var_name = linha[6:].strip()
            if var_name not in variaveis_alocadas:
                variaveis_alocadas.append(var_name)
                secao_dados.append(f"{var_name} times 32 db 0") # Aloca 32 bytes pra variável
            codigo_asm.append(f"    mov di, {var_name}")
            codigo_asm.append("    call _sys_input")

        # Comando: if variavel == "texto": ou elif ...
        elif linha.startswith("if ") or linha.startswith("elif "):
            is_elif = linha.startswith("elif ")
            
            # Se for elif, finaliza a condição anterior e conecta na mesma "corrente" (chain)
            if is_elif and pilha_blocos:
                bloco_antigo = pilha_blocos.pop()
                codigo_asm.append(f"    jmp __end_chain_{bloco_antigo['id_chain']}")
                if bloco_antigo['id_cond'] is not None:
                    codigo_asm.append(f"__end_cond_{bloco_antigo['id_cond']}:")
                chain_id = bloco_antigo['id_chain']
            else:
                chain_id = contador_ifs
                
            partes = linha.replace("if ", "").replace("elif ", "").replace(":", "").split("==")
            if len(partes) == 2:
                var_name = partes[0].strip()
                valor = partes[1].strip().strip('"')
                
                nome_string = f"str_{contador_strings}"
                contador_strings += 1
                secao_dados.append(f'{nome_string} db "{valor}", 0')
                
                cond_id = contador_ifs
                contador_ifs += 1
                
                pilha_blocos.append({
                    'id_chain': chain_id, 
                    'id_cond': cond_id, 
                    'indent': indentacao, 
                    'type': 'elif' if is_elif else 'if'
                })
                
                codigo_asm.append(f"    mov si, {var_name}")
                codigo_asm.append(f"    mov di, {nome_string}")
                codigo_asm.append("    call _sys_strcmp")
                codigo_asm.append("    cmp ax, 1")
                codigo_asm.append(f"    jne __end_cond_{cond_id}")

        # Comando: else:
        elif linha.startswith("else:"):
            if pilha_blocos:
                bloco_antigo = pilha_blocos.pop()
                codigo_asm.append(f"    jmp __end_chain_{bloco_antigo['id_chain']}")
                if bloco_antigo['id_cond'] is not None:
                    codigo_asm.append(f"__end_cond_{bloco_antigo['id_cond']}:")
                
                pilha_blocos.append({
                    'id_chain': bloco_antigo['id_chain'], 
                    'id_cond': None, 
                    'indent': indentacao, 
                    'type': 'else'
                })

        # Comando: func nome:
        elif linha.startswith("func ") and linha.endswith(":"):
            nome_func = linha[5:-1].strip()
            codigo_asm.append(f"\n{nome_func}:")

        # Comando: jmp nome
        elif linha.startswith("jmp "):
            destino = linha[4:].strip()
            codigo_asm.append(f"    jmp {destino}")

        # Comandos: set
        elif linha.startswith("set "):
            if "mode video" in linha:
                codigo_asm.append("    mov ax, 0x0013\n    int 0x10")
            elif "mode text" in linha:
                codigo_asm.append("    mov ax, 0x0003\n    int 0x10")
            elif "init 0" in linha:
                codigo_asm.append("    cli\n    hlt")

    # Fecha qualquer bloco if que tenha ficado aberto no final do arquivo
    while pilha_blocos:
        bloco = pilha_blocos.pop()
        if bloco['id_cond'] is not None:
            codigo_asm.append(f"__end_cond_{bloco['id_cond']}:")
        codigo_asm.append(f"__end_chain_{bloco['id_chain']}:")

    # -----------------------------------------
    # KERNEL CORE FUNCS (O "Coração" do GyalOS)
    # -----------------------------------------
    codigo_asm.extend([
        "",
        "; --- KERNEL CORE FUNCS ---",
        "_sys_halt:",
        "    jmp $",
        "",
        "; Função de Print",
        "_sys_print:",
        "    mov ah, 0x0E",
        ".loop_print:",
        "    lodsb",
        "    cmp al, 0",
        "    je .done_print",
        "    int 0x10",
        "    jmp .loop_print",
        ".done_print:",
        "    ret",
        "",
        "; Função de Input",
        "_sys_input:",
        "    pusha",
        ".loop_input:",
        "    mov ah, 0x00",
        "    int 0x16",
        "    cmp al, 0x0D",      # Tecla Enter?
        "    je .done_input",
        "    mov ah, 0x0E",
        "    int 0x10",          # Mostra a letra
        "    stosb",             # Salva na variável
        "    jmp .loop_input",
        ".done_input:",
        "    mov al, 0",
        "    stosb",
        "    mov ah, 0x0E",
        "    mov al, 13",
        "    int 0x10",
        "    mov al, 10",
        "    int 0x10",
        "    popa",
        "    ret",
        "",
        "; Função de Comparação de Strings",
        "_sys_strcmp:",
        "    pusha",
        ".loop_cmp:",
        "    mov al, byte [si]",
        "    mov bl, byte [di]",
        "    cmp al, bl",
        "    jne .diff_cmp",
        "    cmp al, 0",
        "    je .same_cmp",
        "    inc si",
        "    inc di",
        "    jmp .loop_cmp",
        ".diff_cmp:",
        "    popa",
        "    mov ax, 0",         # Falso
        "    ret",
        ".same_cmp:",
        "    popa",
        "    mov ax, 1",         # Verdadeiro
        "    ret",
        ""
    ])

    # Adiciona as variáveis
    codigo_asm.extend(["; --- DATA SECTION ---"])
    codigo_asm.extend(secao_dados)

    # Assinatura de Boot (Exatamente 512 bytes)
    codigo_asm.extend([
        "",
        "times 510-($-$$) db 0",
        "dw 0xAA55"
    ])

    with open(arquivo_saida, 'w') as f:
        f.write("\n".join(codigo_asm))
    
    print(f"Sucesso! Compilado para {arquivo_saida}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python gyalc.py <entrada.gyal> <saida.asm>")
    else:
        compilar_gyal(sys.argv[1], sys.argv[2])