@echo off
echo ========================================
echo  Iniciando API de Cadastro de Alunos
echo ========================================
echo.

echo [1/3] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Docker nao encontrado. Por favor, instale o Docker Desktop.
    pause
    exit /b 1
)
echo OK - Docker instalado
echo.

echo [2/3] Subindo container da API...
docker compose up -d --build
if %errorlevel% neq 0 (
    echo ERRO: Falha ao subir o container.
    pause
    exit /b 1
)
echo OK - Container rodando
echo.

echo [3/3] Aguardando API inicializar...
timeout /t 3 /nobreak >nul
echo.

echo ========================================
echo  API rodando em: http://127.0.0.1:8000
echo  Documentacao: http://127.0.0.1:8000/docs
echo ========================================
echo.

echo ========================================
echo  ANALISE DE TRAFEGO - Headers HTTP
echo  (equivale ao que o Wireshark mostra
echo   na camada de aplicacao HTTP)
echo ========================================
echo.

echo [curl] POST /alunos - criando aluno e inspecionando headers...
echo Requisicao enviada:
echo   POST /alunos HTTP/1.1
echo   Content-Type: application/json
echo   Body: {"nome":"Aluno Demo","matricula":"0000","curso":"Redes"}
echo.
curl -i -s -X POST http://127.0.0.1:8000/alunos ^
  -H "Content-Type: application/json" ^
  -d "{\"nome\":\"Aluno Demo\",\"matricula\":\"0000\",\"curso\":\"Redes\"}"
echo.
echo.

echo [curl] GET /alunos - listando todos (ver headers de resposta)...
curl -i -s http://127.0.0.1:8000/alunos
echo.
echo.

echo [curl] GET /alunos/9999 - forcando erro 404 (ver headers de erro)...
curl -i -s http://127.0.0.1:8000/alunos/9999
echo.
echo.

echo ========================================
echo  Analise concluida.
echo  Observe nos blocos acima:
echo    - Status line: HTTP/1.1 201 Created
echo    - Header: content-type: application/json
echo    - Header: content-length: (tamanho do corpo)
echo    - Corpo JSON separado dos headers por linha em branco
echo ========================================
echo.

echo Deseja rodar o cliente de teste? (S/N)
set /p run_client="> "
if /i "%run_client%"=="S" (
    echo.
    echo Executando cliente...
    python client.py --host 127.0.0.1 --port 8000
)

echo.
echo Para parar o projeto, execute: stop.bat
pause