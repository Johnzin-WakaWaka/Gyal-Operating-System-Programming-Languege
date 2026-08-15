# Gyal-Operating-System-Programming-Languege

Bem vindos (as) ao repositório original do Gyal.
O Gyal é um projeto de uma Linguagem de Programação de baixo nivel onde o objetivo é criar sistemas operacionais misturando a sintaxe do Python, Assembly, Rust e Bash e tambem tem um sistema operacional chamado Gyal OS

### Como eu fiz?
Basicamnete eu projetei a linguagem, criei a sintaxe, os elementos e tudo e eu usei a [Vorbrix](https://www.vorbrix.app) para criar o compillador (Que EM BREVE vai ser atualizado)

## Estrutura do Projeto

```
 / (pasta raiz)
 |---- Config.conf (Arquivo de configuração)
 |---- gyalc.py (Converte o Gyal pra Assembly)
 |---- build.sh (Compillador / Makefile)
 |
 |---- src (aonde ficaria as imagens e sons (feature futura))
 |---- sys (aonde fica os binários, assemblys e etc)
 |---- gyal (aonde fica os códigos .gyal)
 |---- iso (aonde a iso compillada vai ficar)
 |---- isodir (aonde o .img provisório)
```

**O que vai ter na Versão FINAL da Linguagem (0.0.0.1)**
**Variaveis -----------**
Como se declara uma variavel
```
var <type> nome = valor
```
OBS: o nome NÃO pode ter espaços e nem pontuação

**Tipos de variaveis -----------**
```
boolean - Verdadeira, Falsa ou Nula
char - Basicamente uma string
hex - Para bootloaders e kernels (Exemplo assembly: db 0xAA55)
num - numeros ou pi
```
**Função -----------**
Como se declara uma função
```
func exemplo:
  var char sysname = "Haicai"
```
É basicamente declarar uma função no assembly

**Classe ----------**

Pode ser usada para diferenciar o codigo do bootloader e do kernel
Como se declara uma classe
```
class Saka(variável1, variavel2):
  func exemplo:
    var char sysname = "Haicai"
```
É basicamente declarar uma função em python mas a inicial do nome TEM que tar em maiuscula

**Set ---------**

Set é um comando que define modo de texto e video, estado do sistema (desligado ou na ativa tipo o init 0 do linux), sistema de arquivos
```
set mode text (80x25)
set mode video char <Resolução> (para terminais)
set mode video graph <Resolução> (para interfaçes)
set init 0 (desligado)
set init 1 (bootando | modo real)
set init 2 (ativo | modo protegido)
set filesys <Sistema de arquivos)
```
**Jmp -------**

Jmp é um comando usado em funções que pula pra outra função
Exemplo:
```
func exemplo:
  var char sysname = "Haicai"
  jmp yama

func yama:
  set mode video 300x220
```

**Allocate ---------**

É um comando que cria, aloca, deleta bytes e tem a propiedade dos arquivos e pastas

Exemplo Arquivos:
```
allocate create file "tananam.txt"
allocate delete file "tananam.txt"
allocate rename file "tananam.txt" "xah.txt"
allocate move file "xah.txt" "/test"
allocate copy file "xah.txt" "/test"
```
Exemplo Diretórios:
```
allocate create folder "test"
allocate delete folder "test"
allocate rename folder "test" "aryah"
allocate move folder "aryah" "/home"
allocate copy folder "aryah" "/home"

allocate list (lista os arquivos no direrório atual sem precisar de print)

allocate list <diretório> (lista os arquivos em uma pasta sem precisar de print)
```
**Nav --------**

O nav funciona basicamente como o comando cd do linux
```
nav go "/sys"
```
**Device -------**

Device é o comando que detecta e interage com Teclados, Mouses, Antenas Wi-fi e etc
```
device scan all
device connect keyboard (wifi, moose e etc)
```

**Include --------**
Inculi outros arquivos .gyal e .py para interfaçe tkinter
Exemplo:
```
include "kernel.gyal"
include "desktop.py"
```
**Async ---------**
É o comando multi tarefa:
```
async kill <processo>
async list (lista os processos sem precisar de print)
```
**Outros comandos --------**
print - funciona que nem o print normal do python, só que exibe coisas no modo texto (e video se o terminal tiver no modo video char)
input - Escencial para terminais e elementos de interfaçes para interagir entre interfaçe e kernel
If, else e elif (Ideais para criar terminais)
Dentre outros comandos python que vai tar na documentação final

**Compatibilidade com Python -------**
Bibliotecas:
tkinter (tela cheia para desktops e se não janelas dentro do desktop), pillow, time, datatime, os, subprocess, numpy, matplotlib, keyboard, pygame (criar jogos na interfaçe) e pip

**Estrutura de projetos ---------**

iso - aonde fica a .iso compillada
sys - pasta que tudo que teria na ISO
gyal - pasta de todos os arquivos .gyal que é o bootloader e kernel e etc
src - pasta de imagens e audios que o .gyal usa (Lembrando isso vai tar codificado em hexadecimal na ISO então isso não é visivel no sistema e nem as interfaçes vão ler)
Config.conf - Arquivo de configuração do projeto

**Arquivo de Configuração -----------**

Estrutura do arquivo:

```
[project]
name = "Gyal Project"
version = "0.0.0.1"
author = "Omochain"
description = "Meu primeiro sistema operacional"

[build]
target = "x86"          # Arquitetura (32 ou 64 bits)
output = "iso/gyal.iso" # Onde a ISO vai ser gerada
entry_point = "gyal/boot.gyal" # O arquivo principal que dá o boot
```

**Compillador ----------

É um assembler? (Se é que dá pra considerar assim)
Basicamente ele converte o .gyal para assembly e cria um "core .iso" que usando a pasta sys pra botar tudo dentro da iso e os .py fica nela. Daí o core tem a propiedade de interpretar o python (Tipo um shell python dentro da iso) e con isso funcioba as interfaçes e etc
