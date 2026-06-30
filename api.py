"""
API HTTP de Cadastro de Alunos
---------------------------------
Trabalho de Redes - Tema 2: API HTTP com cliente próprio
(versão: domínio "alunos", containerizada, servida em servidor remoto)

Demonstra na prática:
- Métodos HTTP: GET, POST, PUT, DELETE
- Códigos de status: 200, 201, 204, 404, 422
- JSON como formato de troca de dados
- Statelessness: cada requisição é independente; o servidor não guarda
  sessão do cliente entre chamadas.

Como rodar (local, sem Docker):
    pip install -r requirements.txt
    uvicorn api:app --host 0.0.0.0 --port 8000

Como rodar via Docker: ver README.md
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(
    title="API de Alunos",
    description="API REST simples para cadastro de alunos (CRUD).",
    version="1.0.0",
)

# "Banco de dados" em memória (limitação: zera ao reiniciar o container)
alunos: dict[int, dict] = {}
proximo_id = 1


class AlunoEntrada(BaseModel):
    nome: str
    matricula: str
    curso: str
    ativo: bool = True


class AlunoAtualizacao(BaseModel):
    nome: Optional[str] = None
    matricula: Optional[str] = None
    curso: Optional[str] = None
    ativo: Optional[bool] = None


@app.get("/")
def raiz():
    return {"mensagem": "API de Alunos no ar. Acesse /docs para a documentação."}


@app.get("/alunos")
def listar_alunos(ativo: Optional[bool] = None, curso: Optional[str] = None):
    """
    GET /alunos                  -> lista todos
    GET /alunos?ativo=true       -> filtra por status (query param)
    GET /alunos?curso=Engenharia -> filtra por curso (query param)
    """
    resultado = list(alunos.values())
    if ativo is not None:
        resultado = [a for a in resultado if a["ativo"] == ativo]
    if curso is not None:
        resultado = [a for a in resultado if a["curso"].lower() == curso.lower()]
    return resultado


@app.get("/alunos/{aluno_id}")
def obter_aluno(aluno_id: int):
    if aluno_id not in alunos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return alunos[aluno_id]


@app.post("/alunos", status_code=status.HTTP_201_CREATED)
def criar_aluno(aluno: AlunoEntrada):
    global proximo_id
    novo = {
        "id": proximo_id,
        "nome": aluno.nome,
        "matricula": aluno.matricula,
        "curso": aluno.curso,
        "ativo": aluno.ativo,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
    }
    alunos[proximo_id] = novo
    proximo_id += 1
    return novo


@app.put("/alunos/{aluno_id}")
def atualizar_aluno(aluno_id: int, dados: AlunoAtualizacao):
    if aluno_id not in alunos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    aluno = alunos[aluno_id]
    if dados.nome is not None:
        aluno["nome"] = dados.nome
    if dados.matricula is not None:
        aluno["matricula"] = dados.matricula
    if dados.curso is not None:
        aluno["curso"] = dados.curso
    if dados.ativo is not None:
        aluno["ativo"] = dados.ativo
    return aluno


@app.delete("/alunos/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_aluno(aluno_id: int):
    if aluno_id not in alunos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    del alunos[aluno_id]
    return None
