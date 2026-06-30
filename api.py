"""
API HTTP de Cadastro de Tarefas (To-Do)
----------------------------------------
Trabalho de Redes - Tema 2: API HTTP com cliente próprio

Demonstra na prática:
- Métodos HTTP: GET, POST, PUT, DELETE
- Códigos de status: 200, 201, 204, 404, 422
- JSON como formato de troca de dados
- Statelessness: cada requisição é independente, o servidor não guarda
  "sessão" do cliente entre chamadas (o estado das tarefas fica no servidor,
  mas nenhuma informação sobre QUEM fez a requisição anterior é mantida)

Como rodar:
    pip install fastapi uvicorn
    uvicorn api:app --reload --port 8000

Documentação interativa (Swagger UI) gerada automaticamente em:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(
    title="API de Tarefas",
    description="API REST simples para cadastro de tarefas (CRUD).",
    version="1.0.0",
)

# "Banco de dados" em memória (limitação: zera ao reiniciar o servidor)
tarefas: dict[int, dict] = {}
proximo_id = 1


class TarefaEntrada(BaseModel):
    titulo: str
    concluida: bool = False


class TarefaAtualizacao(BaseModel):
    titulo: Optional[str] = None
    concluida: Optional[bool] = None


@app.get("/")
def raiz():
    return {"mensagem": "API de Tarefas no ar. Acesse /docs para a documentação."}


@app.get("/tarefas")
def listar_tarefas(concluida: Optional[bool] = None):
    """
    GET /tarefas              -> lista todas
    GET /tarefas?concluida=true  -> filtra por status (query param)
    """
    if concluida is None:
        return list(tarefas.values())
    return [t for t in tarefas.values() if t["concluida"] == concluida]


@app.get("/tarefas/{tarefa_id}")
def obter_tarefa(tarefa_id: int):
    if tarefa_id not in tarefas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    return tarefas[tarefa_id]


@app.post("/tarefas", status_code=status.HTTP_201_CREATED)
def criar_tarefa(tarefa: TarefaEntrada):
    global proximo_id
    nova = {
        "id": proximo_id,
        "titulo": tarefa.titulo,
        "concluida": tarefa.concluida,
        "criada_em": datetime.now().isoformat(timespec="seconds"),
    }
    tarefas[proximo_id] = nova
    proximo_id += 1
    return nova


@app.put("/tarefas/{tarefa_id}")
def atualizar_tarefa(tarefa_id: int, dados: TarefaAtualizacao):
    if tarefa_id not in tarefas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")

    tarefa = tarefas[tarefa_id]
    if dados.titulo is not None:
        tarefa["titulo"] = dados.titulo
    if dados.concluida is not None:
        tarefa["concluida"] = dados.concluida
    return tarefa


@app.delete("/tarefas/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_tarefa(tarefa_id: int):
    if tarefa_id not in tarefas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    del tarefas[tarefa_id]
    return None
