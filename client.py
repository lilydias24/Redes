"""
Cliente HTTP para a API de Alunos (servidor remoto)
-------------------------------------------------------
Trabalho de Redes: API HTTP com cliente próprio

Consome a API rodando em outra máquina (servidor remoto, containerizada
com Docker), usando a biblioteca `requests`.
"""

import argparse
import os
import sys
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.json import JSON
from rich import box
from rich.text import Text

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


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
console = Console()


def exibir_header(titulo: str, subtitulo: str = ""):
    """Exibe um cabeçalho colorido para cada seção"""
    texto = Text()
    texto.append(titulo, style="bold cyan")
    if subtitulo:
        texto.append(f"\n{subtitulo}", style="dim")
    console.print(Panel(texto, box=box.DOUBLE, border_style="cyan"))


def exibir_status(status_code: int):
    """Exibe o status code com cores baseadas no tipo"""
    if 200 <= status_code < 300:
        cor = "green"
        emoji = "✓"
    elif 400 <= status_code < 500:
        cor = "yellow"
        emoji = "⚠"
    else:
        cor = "red"
        emoji = "✗"

    console.print(f"{emoji} [bold {cor}]Status: {status_code}[/bold {cor}]")


def exibir_json(data):
    """Exibe JSON formatado e colorido"""
    console.print(JSON.from_data(data))


def exibir_headers_resposta(r: requests.Response):
    """
    Exibe os headers HTTP da resposta — equivale ao que o Wireshark mostraria
    na camada de aplicação (status line + headers relevantes).
    """
    table = Table(
        title="📡 Headers HTTP da Resposta",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold yellow",
        border_style="yellow",
    )
    table.add_column("Header", style="yellow", no_wrap=True)
    table.add_column("Valor", style="white")

    # Sempre exibe esses três se existirem; outros são opcionais
    priority = ["content-type", "content-length", "date", "server"]
    seen = set()
    for h in priority:
        if h in r.headers:
            table.add_row(h, r.headers[h])
            seen.add(h)
    # demais headers extras (ex.: x-process-time da FastAPI)
    for k, v in r.headers.items():
        if k.lower() not in seen:
            table.add_row(k.lower(), v)

    console.print(table)


def criar_tabela_alunos(alunos: list):
    """Cria uma tabela formatada com dados dos alunos"""
    if not alunos:
        console.print("[dim]Nenhum aluno cadastrado[/dim]")
        return

    table = Table(title="Alunos Cadastrados", box=box.ROUNDED, show_header=True,
                  header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="center")
    table.add_column("Nome", style="green")
    table.add_column("Matrícula", style="yellow")
    table.add_column("Curso", style="blue")
    table.add_column("Ativo", justify="center")
    table.add_column("Criado em", style="dim")

    for aluno in alunos:
        ativo_emoji = "✓" if aluno.get("ativo", True) else "✗"
        table.add_row(
            str(aluno.get("id", "")),
            aluno.get("nome", ""),
            aluno.get("matricula", ""),
            aluno.get("curso", ""),
            ativo_emoji,
            aluno.get("criado_em", "")[:10] if aluno.get("criado_em") else ""
        )

    console.print(table)


def main():
    console.print(Panel.fit(
        f"[bold green]Conectando à API em:[/bold green] [cyan]{BASE_URL}[/cyan]",
        border_style="green"
    ))
    console.print()

    # 1. GET /alunos (lista vazia)
    exibir_header("1. GET /alunos", "Listando alunos (inicialmente vazio)")
    r = requests.get(f"{BASE_URL}/alunos")
    exibir_status(r.status_code)
    criar_tabela_alunos(r.json())
    console.print()

    # 2. POST /alunos (cadastrando alunos)
    exibir_header("2. POST /alunos", "Cadastrando 3 novos alunos")
    novos_alunos = [
        {"nome": "Arthur Parizotto", "matricula": "2021001", "curso": "Engenharia de Software"},
        {"nome": "Maria Eduarda Sanchez", "matricula": "2021002", "curso": "Engenharia de Software"},
        {"nome": "Guilherme Souza", "matricula": "2021003", "curso": "Ciência da Computação"},
    ]
    ids_criados = []
    primeiro = True
    for aluno in novos_alunos:
        r = requests.post(f"{BASE_URL}/alunos", json=aluno)
        exibir_status(r.status_code)
        console.print(f"[green]✓ Aluno criado:[/green] [bold]{aluno['nome']}[/bold]")
        exibir_json(r.json())
        # Exibe headers apenas na 1ª criação para não repetir desnecessariamente
        if primeiro:
            exibir_headers_resposta(r)
            console.print(
                "[dim]  ^ Content-Type confirma JSON; Content-Length = tamanho do corpo em bytes[/dim]"
            )
            primeiro = False
        console.print()
        ids_criados.append(r.json()["id"])

    # 3. GET /alunos/{id} (buscar específico)
    exibir_header("3. GET /alunos/{id}", f"Buscando aluno com ID {ids_criados[0]}")
    r = requests.get(f"{BASE_URL}/alunos/{ids_criados[0]}")
    exibir_status(r.status_code)
    exibir_json(r.json())
    console.print()

    # 4. PUT /alunos/{id} (atualizar)
    exibir_header("4. PUT /alunos/{id}", "Atualizando curso do aluno")
    r = requests.put(
        f"{BASE_URL}/alunos/{ids_criados[0]}",
        json={"curso": "Engenharia de Computação"},
    )
    exibir_status(r.status_code)
    console.print("[yellow]📝 Curso atualizado:[/yellow]")
    exibir_json(r.json())
    console.print()

    # 5. GET /alunos?curso= (filtro)
    exibir_header("5. GET /alunos?curso=", "Filtrando por curso: Ciência da Computação")
    r = requests.get(f"{BASE_URL}/alunos", params={"curso": "Ciência da Computação"})
    exibir_status(r.status_code)
    criar_tabela_alunos(r.json())
    console.print()

    # 6. DELETE /alunos/{id}
    exibir_header("6. DELETE /alunos/{id}", f"Removendo aluno ID {ids_criados[-1]}")
    r = requests.delete(f"{BASE_URL}/alunos/{ids_criados[-1]}")
    exibir_status(r.status_code)
    console.print("[red]🗑️  Aluno removido (204 = sem corpo de resposta)[/red]")
    exibir_headers_resposta(r)
    console.print("[dim]  ^ 204 No Content: status line confirma sucesso, mas corpo está ausente[/dim]")
    console.print()

    # 7. Erro 404
    exibir_header("7. GET /alunos/{id}", "Testando erro 404 - ID inexistente (9999)")
    r = requests.get(f"{BASE_URL}/alunos/9999")
    exibir_status(r.status_code)
    exibir_json(r.json())
    exibir_headers_resposta(r)
    console.print("[dim]  ^ Mesmo em erro, o servidor responde JSON com Content-Type correto[/dim]")
    console.print()

    # 8. Erro 422
    exibir_header("8. POST /alunos", "Testando erro 422 - corpo inválido")
    r = requests.post(f"{BASE_URL}/alunos", json={"nome": "Sem matrícula nem curso"})
    exibir_status(r.status_code)
    exibir_json(r.json())
    console.print()

    # Fim
    console.print(Panel.fit(
        "[bold green]✓ Demonstração concluída com sucesso![/bold green]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()