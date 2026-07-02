@echo off
echo ========================================
echo  Parando API de Cadastro de Alunos
echo ========================================
echo.

echo Parando e removendo containers...
docker compose down

if %errorlevel% equ 0 (
    echo.
    echo OK - Projeto parado com sucesso!
) else (
    echo.
    echo ERRO: Falha ao parar o projeto.
)

echo.
pause
