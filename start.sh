#!/bin/bash

echo "========================================"
echo " Iniciando API de Cadastro de Alunos"
echo "========================================"
echo

echo "[1/3] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker não encontrado. Por favor, instale o Docker."
    exit 1
fi
echo "OK - Docker instalado"
echo

echo "[2/3] Subindo container da API..."
docker compose up -d --build
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao subir o container."
    exit 1
fi
echo "OK - Container rodando"
echo

echo "[3/3] Aguardando API inicializar..."
sleep 3
echo

echo "========================================"
echo " API rodando em: http://127.0.0.1:8000"
echo " Documentação: http://127.0.0.1:8000/docs"
echo "========================================"
echo

read -p "Deseja rodar o cliente de teste? (s/n): " run_client
if [[ $run_client == "s" || $run_client == "S" ]]; then
    echo
    echo "Executando cliente..."
    python3 client.py --host 127.0.0.1 --port 8000
fi

echo
echo "Para parar o projeto, execute: ./stop.sh"
