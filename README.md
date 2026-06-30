# API HTTP com Cliente Próprio — Cadastro de Alunos (Docker + Servidor Remoto)

**Trabalho de Redes — Tema 2**

API REST de cadastro de alunos, construída com **FastAPI**, empacotada em
**Docker** e pensada para rodar em um **servidor remoto** (uma VM, um VPS, ou
qualquer outra máquina da rede). O cliente, em Python (**requests**), roda na
sua máquina local e consome a API através da rede.

---

## 1. Estrutura do projeto

```
api-alunos-docker/
├── api.py              # servidor (API)
├── client.py            # cliente que consome a API remota
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
└── README.md
```

## 2. Arquitetura da demonstração

```
[ Seu notebook ]                          [ Servidor remoto ]
   client.py    ----HTTP (porta 8000)---->   container Docker
   (requests)                                 rodando api.py (FastAPI)
```

O cliente roda localmente; o servidor roda em outra máquina, dentro de um
container. Isso é o que torna a demonstração de rede mais real: existe
tráfego de fato saindo da sua máquina até outro host.

---

## 3. Subindo a API no servidor remoto

### Pré-requisitos no servidor remoto
- Acesso via SSH
- Docker e Docker Compose instalados (`docker --version` / `docker compose version`)
- Porta 8000 liberada no firewall/security group (se for nuvem, ex.: AWS/GCP/Azure,
  precisa liberar a porta 8000 de entrada nas regras de rede)

### Passo 1 — Copiar o projeto para o servidor
Do seu notebook:
```bash
scp -r api-alunos-docker usuario@IP_DO_SERVIDOR:~/
```

### Passo 2 — Conectar via SSH e subir o container
```bash
ssh usuario@IP_DO_SERVIDOR
cd api-alunos-docker
docker compose up -d --build
```
Isso builda a imagem (`Dockerfile`) e sobe o container expondo a porta `8000`.

### Passo 3 — Verificar que está no ar
Ainda no servidor (ou de outra máquina, se a porta estiver liberada):
```bash
curl -i http://localhost:8000/
docker ps          # confirma o container "api-alunos" rodando
docker logs api-alunos -f   # acompanha os logs em tempo real (bom pro vídeo)
```

> **Sem Docker Compose?** Alternativa com Docker puro:
> ```bash
> docker build -t api-alunos .
> docker run -d --name api-alunos -p 8000:8000 api-alunos
> ```

---

## 4. Rodando o cliente (na sua máquina local)

```bash
pip install requests
python client.py --host IP_DO_SERVIDOR --port 8000
```
ou, usando variável de ambiente:
```bash
export API_HOST=IP_DO_SERVIDOR
python client.py
```

O cliente cadastra, lista, atualiza, filtra e remove alunos, imprimindo o
status code e o corpo de cada resposta — tudo isso indo até o servidor
remoto pela rede.

### Testando localmente antes de ir pro servidor remoto
```bash
docker compose up -d --build
python client.py --host 127.0.0.1 --port 8000
```

---

## 5. Demonstração prática (roteiro para o vídeo)

1. Mostrar o `docker compose up -d --build` rodando no servidor remoto via SSH.
2. `docker ps` mostrando o container ativo.
3. Rodar `client.py --host IP_DO_SERVIDOR` no notebook, comentando cada
   chamada (POST criando alunos, GET listando/filtrando, PUT atualizando,
   DELETE removendo, e os erros 404/422).
4. Repetir uma chamada com `curl` direto pro IP remoto, pra mostrar a
   requisição "crua":
   ```bash
   curl -i http://IP_DO_SERVIDOR:8000/alunos
   ```
5. Mostrar a resolução de nome e a conectividade até o servidor (seção 6).
6. Mostrar a captura de tráfego no Wireshark (seção 7).

---

## 6. `dig` e `iperf3` (fazem sentido agora, com servidor remoto)

### `dig` — resolução de nome
Se o servidor remoto tiver um domínio/hostname (em vez de só IP), dá pra
mostrar a resolução DNS antes da conexão:
```bash
dig meuservidor.exemplo.com
```
Isso evidencia o passo que falta quando se usa só IP direto: o cliente
precisa primeiro traduzir o nome em IP via DNS antes de abrir a conexão TCP
com a API.

### `iperf3` — desempenho de rede entre cliente e servidor
No servidor remoto (modo servidor):
```bash
iperf3 -s
```
No cliente, do seu notebook (modo cliente):
```bash
iperf3 -c IP_DO_SERVIDOR
```
Isso mostra a largura de banda real disponível entre as duas máquinas —
útil para comentar no vídeo se a latência/throughput observada na API tem
relação com a qualidade do link de rede.

---

## 7. Captura e análise de tráfego (Wireshark)

Como agora cliente e servidor estão em máquinas diferentes, a captura deve
ser feita na interface de rede real do seu notebook (Wi-Fi/Ethernet), e não
mais no loopback.

1. Abrir o Wireshark e selecionar a interface de rede usada para sair à
   internet (Wi-Fi ou Ethernet).
2. Aplicar o filtro:
   ```
   ip.addr == IP_DO_SERVIDOR && tcp.port == 8000
   ```
3. Com a captura rodando, executar `client.py` apontando para o servidor
   remoto.
4. No vídeo, mostrar:
   - O **three-way handshake** TCP (SYN, SYN-ACK, ACK) com o IP remoto.
   - A requisição HTTP (`POST /alunos HTTP/1.1`), headers (`Host`,
     `Content-Type`, `Content-Length`) e corpo em JSON.
   - A resposta (`HTTP/1.1 201 Created`), headers e corpo JSON.
   - "Follow → HTTP Stream" para ver requisição + resposta juntas.
   - Se tiver rodado `dig` antes, também dá pra mostrar a consulta DNS
     (filtro `dns`) acontecendo antes do handshake TCP.

---

## 8. Conceitos (explicação curta)

- **HTTP**: protocolo de aplicação usado pelo `client.py`/`curl` para se
  comunicar com a API (`api.py`) rodando no servidor remoto, seguindo o
  modelo requisição-resposta.
- **Métodos HTTP**: `GET` (ler), `POST` (criar), `PUT` (atualizar),
  `DELETE` (remover).
- **Códigos de status**: `200 OK`, `201 Created`, `204 No Content`,
  `404 Not Found`, `422 Unprocessable Entity` (corpo inválido).
- **JSON**: formato de troca de dados entre cliente e servidor.
- **Statelessness**: cada requisição é processada de forma independente; o
  servidor não guarda sessão do cliente entre chamadas — só os dados dos
  alunos ficam armazenados no lado do servidor.
- **Containers (Docker)**: a API roda isolada em um container, com suas
  dependências (`requirements.txt`) empacotadas na imagem — o mesmo
  container roda igual em qualquer máquina com Docker, o que facilita subir
  no servidor remoto sem se preocupar com versão de Python/bibliotecas
  instaladas na máquina host.
- **Mapeamento de porta**: o `-p 8000:8000` (ou a seção `ports` no
  compose) conecta a porta 8000 do container à porta 8000 do servidor
  remoto, é isso que permite o cliente externo acessar a API.

---

## 9. Limitações do experimento

- **Sem persistência real**: alunos ficam em um dicionário em memória —
  reiniciar o container apaga todos os dados (não há banco de dados).
- **Ausência de segurança real**: API em HTTP puro (sem TLS/HTTPS), sem
  autenticação/autorização. Qualquer um que souber o IP e a porta consegue
  acessar a API.
- **Rede real, mas ainda controlada**: o teste depende da qualidade do
  link entre o notebook e o servidor remoto (Wi-Fi, provedor, distância);
  os resultados de `iperf3` e a captura podem variar bastante dependendo
  de onde o servidor remoto está hospedado.
- **Poucos clientes**: a demonstração usa um único cliente sequencial; não
  há teste de concorrência ou carga.
- **Um único container/réplica**: não há balanceamento de carga nem
  múltiplas instâncias da API — só um container rodando.
