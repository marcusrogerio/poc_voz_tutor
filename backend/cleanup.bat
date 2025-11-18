@echo off
echo ==========================================================
echo      CLEAN AIA Voice Engine - Resetando Ambiente
echo ==========================================================
echo.

REM --- Tenta desativar o venv, mesmo corrompido ---
echo Tentando desativar ambiente virtual...
call deactivate 2>nul
set PROMPT=$P$G

REM --- Remove a pasta venv ---
if exist "venv" (
    echo Removendo pasta 'venv'...
    rmdir /s /q "venv"
) else (
    echo Pasta 'venv' nao encontrada. OK.
)

echo.
REM --- Confirma que nao existe mais ---
if exist "venv" (
    echo ERRO: A pasta 'venv' NAO foi removida!
    echo Verifique permissao ou feche programas usando a pasta.
) else (
    echo Ambiente virtual removido com sucesso!
)

echo.
echo ==========================================================
echo Ambiente limpo! Feche este terminal e abra outro.
echo ==========================================================
echo.
pause
