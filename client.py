"""
Cliente HTTP para a API de Tarefas
------------------------------------
Trabalho de Redes - Tema 2: API HTTP com cliente próprio

Este script consome a API (api.py) usando a biblioteca `requests`,
demonstrando na prática os 4 verbos HTTP principais e os códigos
de status retornados pelo servidor.

Como rodar:
    1. Em um terminal, suba a API:
         uvicorn api:app --reload --port 8000
    2. Em outro terminal, rode este cliente:
         pip install requests
         python client.py
"""

import requests

BASE_URL = "http://127.0.0.1:8000"


def linha(titulo: str):
    print(f"\n{'='*60}\n{titulo}\n{'='*60}")


def main():
    linha("1. GET /tarefas (lista vazia no início)")
    r = requests.get(f"{BASE_URL}/tarefas")
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("2. POST /tarefas (criando 3 tarefas)")
    titulos = ["Estudar HTTP", "Revisar TCC", "Configurar Wireshark"]
    ids_criados = []
    for titulo in titulos:
        r = requests.post(f"{BASE_URL}/tarefas", json={"titulo": titulo})
        print(f"Status: {r.status_code} | Criada: {r.json()}")
        ids_criados.append(r.json()["id"])

    linha("3. GET /tarefas/{id} (buscando uma tarefa específica)")
    r = requests.get(f"{BASE_URL}/tarefas/{ids_criados[0]}")
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("4. PUT /tarefas/{id} (marcando a 1ª tarefa como concluída)")
    r = requests.put(
        f"{BASE_URL}/tarefas/{ids_criados[0]}",
        json={"concluida": True},
    )
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("5. GET /tarefas?concluida=true (filtro via query param)")
    r = requests.get(f"{BASE_URL}/tarefas", params={"concluida": True})
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("6. DELETE /tarefas/{id} (removendo a última tarefa)")
    r = requests.delete(f"{BASE_URL}/tarefas/{ids_criados[-1]}")
    print(f"Status: {r.status_code} (204 = sem corpo de resposta)")

    linha("7. GET /tarefas/{id} em ID inexistente (demonstrando erro 404)")
    r = requests.get(f"{BASE_URL}/tarefas/9999")
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("8. POST /tarefas com corpo inválido (demonstrando erro 422)")
    r = requests.post(f"{BASE_URL}/tarefas", json={"concluida": True})  # falta "titulo"
    print(f"Status: {r.status_code}")
    print(f"Corpo:  {r.json()}")

    linha("Fim da demonstração")


if __name__ == "__main__":
    main()
