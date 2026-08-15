#!/bin/bash

echo "🚀 Iniciando a compilação do GyalOS..."

# Cria as pastas necessárias
mkdir -p iso
mkdir -p sys
mkdir -p gyal
mkdir -p isodir # Pasta temporária pra montar a estrutura do CD

echo "⚙️  Traduzindo boot.gyal para Assembly..."
python gyalc.py gyal/boot.gyal sys/boot.asm

if [ $? -ne 0 ]; then
    echo "❌ Erro na tradução do Python!"
    exit 1
fi

echo "🔨 Montando o binário com NASM..."
nasm -f bin sys/boot.asm -o sys/boot.bin

if [ $? -ne 0 ]; then
    echo "❌ Erro na montagem com o NASM!"
    exit 1
fi

echo "📦 Criando imagem de boot..."
# Cria a imagem do disquete e joga dentro da pasta do CD
dd if=/dev/zero of=isodir/floppy.img bs=1024 count=1440 2>/dev/null
dd if=sys/boot.bin of=isodir/floppy.img conv=notrunc 2>/dev/null

echo "💿 Empacotando numa .ISO de verdade..."
# O xorriso pega a pasta isodir e transforma numa ISO bootável oficial!
xorriso -as mkisofs -V "GYAL_OS" -b floppy.img -o iso/gyal.iso isodir/ 2>/dev/null

echo "✅ Sucesso! A sua iso/gyal.iso está pronta!"