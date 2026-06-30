"""
Cliente HTTP para a API de Alunos (servidor remoto)
-------------------------------------------------------
Trabalho de Redes - Tema 2: API HTTP com cliente próprio

Consome a API rodando em outra máquina (servidor remoto, containerizada
com Docker), usando a biblioteca `requests`.

Como rodar:
    pip install requests

    # apontando para o servidor remoto:
    python client.py --host 200.18.x.x --port 8000

    # ou, se preferir, defina a variável de ambiente:
    export API_HOST=200.18.x.x
    python client.py

    # para testar localmente antes de subir no servidor remoto:
    python client.py --host 127.0.0.1
"""

import argparse
import os
import requests


def montar_base_url() -> str:
    parser = argparse.ArgumentParser(description="Cliente da API de Alunos")
    parser.add_argument(
        "--host",
        default=os.environ.get("API_HOST", "127.0.0.1"),
        help="IP ou hostname do servidor remoto (default: 127.0.0.1 ou $API_HOST)",
    )
    parser.add_argument(
        "--port",
        default=os.environ.get("API_PORT", "8000"),
        help="Porta da API (default: 8000 ou $API_PORT)",
    )
    args = parser.parse_args()
    return f"http://{args.host}:{args.port}"


BASE_URL = montar_base_url()


def linha(titulo: str):
    print(f"\n{'='*60}\n{titulo}\n{'='*60}")


def main():
    print(f"Conectando à API em: {BASE_URL}")

    linha("1. GET /alunos (lista vazia no início)")
    r = requests.get(f"{BASE_URL}/alunos")
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("2. POST /alunos (cadastrando 3 alunos)")
    novos_alunos = [
        {"nome": "Arthur Parizotto", "matricula": "2021001", "curso": "Engenharia de Software"},
        {"nome": "Maria Eduarda Sanchez", "matricula": "2021002", "curso": "Engenharia de Software"},
        {"nome": "Guilherme Souza", "matricula": "2021003", "curso": "Ciência da Computação"},
    ]
    ids_criados = []
    for aluno in novos_alunos:
        r = requests.post(f"{BASE_URL}/alunos", json=aluno)
        print(f"Status: {r.status_code} | Criado: {r.json()}")
        ids_criados.append(r.json()["id"])

    linha("3. GET /alunos/{id} (buscando um aluno específico)")
    r = requests.get(f"{BASE_URL}/alunos/{ids_criados[0]}")
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("4. PUT /alunos/{id} (atualizando o curso de um aluno)")
    r = requests.put(
        f"{BASE_URL}/alunos/{ids_criados[0]}",
        json={"curso": "Engenharia de Computação"},
    )
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("5. GET /alunos?curso=Ciência da Computação (filtro via query param)")
    r = requests.get(f"{BASE_URL}/alunos", params={"curso": "Ciência da Computação"})
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("6. DELETE /alunos/{id} (removendo o último aluno cadastrado)")
    r = requests.delete(f"{BASE_URL}/alunos/{ids_criados[-1]}")
    print(f"Status: {r.status_code} (204 = sem corpo de resposta)")

    linha("7. GET /alunos/{id} em ID inexistente (demonstrando erro 404)")
    r = requests.get(f"{BASE_URL}/alunos/9999")
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("8. POST /alunos com corpo inválido (demonstrando erro 422)")
    r = requests.post(f"{BASE_URL}/alunos", json={"nome": "Sem matrícula nem curso"})
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("Fim da demonstração")


if __name__ == "__main__":
    main()
