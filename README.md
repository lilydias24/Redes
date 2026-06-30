# API HTTP com Cliente Próprio — Cadastro de Tarefas

**Trabalho de Redes — Tema 2**

API REST de cadastro de tarefas (to-do list), construída com **FastAPI**, e um
cliente próprio em Python (**requests**) que a consome demonstrando os
principais métodos e conceitos de HTTP.

---

## 1. Estrutura do projeto

```
api-tarefas/
├── api.py        # servidor (API)
├── client.py      # cliente que consome a API
└── README.md
```

## 2. Como rodar (tudo local)

### Pré-requisitos
```bash
pip install fastapi uvicorn requests
```

### Passo 1 — Subir a API
Em um terminal:
```bash
uvicorn api:app --reload --port 8000
```
A API ficará disponível em `http://127.0.0.1:8000`.
Documentação interativa (Swagger) em `http://127.0.0.1:8000/docs`.

### Passo 2 — Rodar o cliente
Em **outro** terminal:
```bash
python client.py
```
O cliente vai criar, listar, atualizar, filtrar e remover tarefas,
imprimindo o status code e o corpo de cada resposta no terminal.

---

## 3. Demonstração prática (roteiro para o vídeo)

1. Mostrar o `api.py` rodando (uvicorn no terminal).
2. Abrir `http://127.0.0.1:8000/docs` no navegador e mostrar os endpoints.
3. Rodar `client.py` e comentar cada chamada (POST criando tarefas, GET
   listando, PUT atualizando, DELETE removendo, e os erros 404/422).
4. Repetir uma ou duas chamadas usando `curl` diretamente, para mostrar a
   requisição "crua" sem o cliente Python (exemplos abaixo).
5. Mostrar a captura de tráfego no Wireshark (seção 4).

### Exemplos com `curl`

```bash
# Listar tarefas
curl -i http://127.0.0.1:8000/tarefas

# Criar uma tarefa
curl -i -X POST http://127.0.0.1:8000/tarefas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Gravar vídeo da entrega"}'

# Atualizar (marcar como concluída)
curl -i -X PUT http://127.0.0.1:8000/tarefas/1 \
  -H "Content-Type: application/json" \
  -d '{"concluida": true}'

# Remover
curl -i -X DELETE http://127.0.0.1:8000/tarefas/1

# Forçar 404 (id que não existe)
curl -i http://127.0.0.1:8000/tarefas/9999
```
A flag `-i` faz o curl mostrar os **headers** da resposta (status line,
`Content-Type`, `Content-Length` etc.), que é justamente o que a captura de
tráfego vai evidenciar no nível de pacote.

---

## 4. Captura e análise de tráfego (Wireshark)

Como tudo roda em `127.0.0.1` (loopback), é preciso capturar na interface
**Loopback** (no Windows: "Npcap Loopback Adapter"; no Linux: `lo`).

1. Abrir o Wireshark e selecionar a interface de loopback.
2. Aplicar o filtro:
   ```
   tcp.port == 8000
   ```
   ou, para ver só o tráfego já reconhecido como HTTP:
   ```
   http
   ```
3. Com a captura rodando, executar `client.py` (ou os comandos `curl` acima).
4. Parar a captura e abrir uma requisição POST, por exemplo. Mostrar no vídeo:
   - O **three-way handshake** TCP (SYN, SYN-ACK, ACK) antes da requisição.
   - A requisição HTTP em si: método (`POST /tarefas HTTP/1.1`), headers
     (`Host`, `Content-Type`, `Content-Length`) e o corpo em JSON.
   - A resposta do servidor: status line (`HTTP/1.1 201 Created`), headers
     e o corpo JSON retornado.
   - Usar "Follow → HTTP Stream" no Wireshark para ver a conversa completa
     (requisição + resposta) de forma legível.

### Alternativa/complemento: `dig`
Como aqui o servidor é local (`127.0.0.1`), não há resolução DNS real para
demonstrar. Para cumprir esse ponto, pode-se rodar:
```bash
dig api.exemplo.com
```
e comentar no vídeo que, em um cenário real (servidor em outro host), o
cliente precisaria primeiro resolver o nome do servidor via DNS antes de
abrir a conexão TCP — passo que não existe quando se usa `127.0.0.1`
diretamente.

---

## 5. Conceitos (explicação curta)

- **HTTP**: protocolo de aplicação usado pelo cliente (`client.py`/`curl`)
  para se comunicar com o servidor (`api.py`), seguindo o modelo
  requisição-resposta.
- **Métodos HTTP**:
  - `GET` — ler dados (listar/buscar tarefas), sem efeito colateral.
  - `POST` — criar um novo recurso (nova tarefa).
  - `PUT` — atualizar um recurso existente.
  - `DELETE` — remover um recurso.
- **Códigos de status** usados na API:
  - `200 OK` — leitura/atualização bem-sucedida.
  - `201 Created` — recurso criado com sucesso (POST).
  - `204 No Content` — remoção bem-sucedida, sem corpo de resposta.
  - `404 Not Found` — tarefa com o ID informado não existe.
  - `422 Unprocessable Entity` — corpo da requisição não passou na
    validação (ex.: faltou o campo `titulo`).
- **JSON**: formato usado tanto para enviar dados ao criar/atualizar
  tarefas quanto para o servidor responder — é o "idioma" comum entre
  cliente e servidor.
- **Statelessness (sem estado)**: cada requisição HTTP é processada de
  forma independente — o servidor não guarda informação de "quem perguntou
  o quê antes". O estado das tarefas fica armazenado no servidor, mas não
  há sessão de cliente: se o cliente fizer duas requisições seguidas, a
  segunda não "lembra" da primeira a não ser pelos dados explícitos
  (ex.: o ID da tarefa).

---

## 6. Limitações do experimento

- **Ambiente local**: cliente e servidor rodam na mesma máquina
  (`127.0.0.1`), então não há latência de rede real nem resolução DNS
  efetiva — em produção, isso aconteceria entre hosts diferentes.
- **Poucos clientes**: a demonstração usa apenas um cliente sequencial;
  não foi testado comportamento sob concorrência (múltiplos clientes
  simultâneos) ou carga.
- **Sem persistência real**: as tarefas ficam em um dicionário em memória
  — qualquer reinício do servidor apaga todos os dados.
- **Ausência de segurança real**: a API usa HTTP puro (sem TLS/HTTPS), sem
  autenticação ou autorização. Em um cenário real, seria necessário usar
  HTTPS e algum mecanismo de autenticação (ex.: API key, OAuth2/JWT).
- **Rede simulada**: como tudo passa pela interface de loopback, a captura
  no Wireshark mostra o tráfego "ideal" (sem perda de pacotes, sem
  retransmissão), o que não reflete condições de rede real.
