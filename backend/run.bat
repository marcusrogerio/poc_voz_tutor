@echo off
echo ==========================================================
echo      AIA Voice Engine v3 - Inicializando Servidor
echo ==========================================================
echo.

REM --- Verifica existencia do venv ---
if not exist "venv" (
    echo ERRO: Ambiente virtual 'venv' NAO existe!
    echo Rode primeiro: install.bat
    pause
    exit /b
)

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Iniciando o servidor FastAPI na porta 8000...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
