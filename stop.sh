#!/bin/bash

echo "========================================"
echo " Parando API de Cadastro de Alunos"
echo "========================================"
echo

echo "Parando e removendo containers..."
docker compose down

if [ $? -eq 0 ]; then
    echo
    echo "OK - Projeto parado com sucesso!"
else
    echo
    echo "ERRO: Falha ao parar o projeto."
fi

echo
