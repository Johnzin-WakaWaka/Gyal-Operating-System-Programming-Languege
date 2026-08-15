; --- GYAL OS COMPILER v0.0.0.1 ---
bits 16
org 0x7C00
jmp _gyal_start

_gyal_start:
    mov ax, 0
    mov ds, ax
    mov es, ax
    mov si, str_0
    call _sys_print
    mov si, str_1
    call _sys_print
    mov di, senha
    call _sys_input
    mov si, senha
    mov di, str_2
    call _sys_strcmp
    cmp ax, 1
    jne __end_cond_0
    mov si, str_3
    call _sys_print
    jmp __end_chain_0
__end_cond_0:
    mov si, str_4
    call _sys_print
    cli
    hlt
__end_chain_0:

; --- KERNEL CORE FUNCS ---
_sys_halt:
    jmp $

; Função de Print
_sys_print:
    mov ah, 0x0E
.loop_print:
    lodsb
    cmp al, 0
    je .done_print
    int 0x10
    jmp .loop_print
.done_print:
    ret

; Função de Input
_sys_input:
    pusha
.loop_input:
    mov ah, 0x00
    int 0x16
    cmp al, 0x0D
    je .done_input
    mov ah, 0x0E
    int 0x10
    stosb
    jmp .loop_input
.done_input:
    mov al, 0
    stosb
    mov ah, 0x0E
    mov al, 13
    int 0x10
    mov al, 10
    int 0x10
    popa
    ret

; Função de Comparação de Strings
_sys_strcmp:
    pusha
.loop_cmp:
    mov al, byte [si]
    mov bl, byte [di]
    cmp al, bl
    jne .diff_cmp
    cmp al, 0
    je .same_cmp
    inc si
    inc di
    jmp .loop_cmp
.diff_cmp:
    popa
    mov ax, 0
    ret
.same_cmp:
    popa
    mov ax, 1
    ret

; --- DATA SECTION ---
str_0 db "--- Login (Se errar o PC desliga) ---", 13, 10, 0
str_1 db "Digite a senha:", 13, 10, 0
senha times 32 db 0
str_2 db "1234", 0
str_3 db "Acesso Liberado! Bem-vindo Omochain!", 13, 10, 0
str_4 db "Senha Incorreta. Sistema travado.", 13, 10, 0

times 510-($-$$) db 0
dw 0xAA55