@echo off
echo ==========================================================
echo        INSTALL AIA Voice Engine - Backend Setup (FORCE)
echo ==========================================================
echo.

REM --- Verifica se Python existe ---
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python 3.10+ e marque "Add to PATH".
    pause
    exit /b
)

REM --- Mostra versao ---
for /f "tokens=2 delims= " %%v in ('python --version') do set PYV=%%v
echo Python detectado: %PYV%
echo.

REM --- Se venv não existe, cria ---
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
) else (
    echo Ambiente virtual ja existe. OK.
)

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Atualizando pip e ferramentas essenciais...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir --force-reinstall

echo.
echo Instalando dependencias com FORCE REINSTALL...
pip install --no-cache-dir --force-reinstall -r requirements.txt

echo.
echo ==========================================================
echo Instalacao concluida com sucesso!
echo Execute: run.bat
echo ==========================================================
echo.
pause
