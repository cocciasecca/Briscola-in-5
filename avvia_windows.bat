@echo off
setlocal
cd /d "%~dp0"

set "NEED_INSTALL=0"
if not exist .venv (
  echo Prima installazione: preparo l'ambiente Python...
  py -3.11 -m venv .venv 2>nul || python -m venv .venv
  set "NEED_INSTALL=1"
)

call .venv\Scripts\activate.bat

if not exist .venv\.briscola5_installata set "NEED_INSTALL=1"
python -c "import fastapi, uvicorn, briscola5" >nul 2>&1 || set "NEED_INSTALL=1"

rem Controlla se pyproject.toml e' piu' recente del marcatore.
if exist .venv\.briscola5_installata (
  powershell -NoProfile -Command "if ((Get-Item 'pyproject.toml').LastWriteTimeUtc -gt (Get-Item '.venv\.briscola5_installata').LastWriteTimeUtc) { exit 1 } else { exit 0 }" >nul 2>&1
  if errorlevel 1 set "NEED_INSTALL=1"
)

if "%NEED_INSTALL%"=="1" (
  echo Installazione/aggiornamento delle dipendenze ^(solo quando necessario^)...
  python -m pip install -e .
  if errorlevel 1 goto :error
  type nul > .venv\.briscola5_installata
)

python -m briscola5.web.main
goto :end

:error
echo.
echo Installazione non riuscita.
pause

:end
endlocal
