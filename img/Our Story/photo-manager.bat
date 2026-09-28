@echo off
rem Our Story photo manager -- double-click this to add, delete and reorder the
rem photos in the Countries / Mexico / States galleries. See _tool\photo_manager.py.

setlocal
cd /d "%~dp0"

set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (
  where py >nul 2>nul && set "PY=py -3"
)
if not defined PY (
  echo Could not find Python on your PATH.
  echo Install Python 3 from https://www.python.org/downloads/ ^(tick "Add to PATH"^),
  echo then double-click this file again.
  echo.
  pause
  exit /b 1
)

%PY% "%~dp0_tool\photo_manager.py" %*
if errorlevel 1 (
  echo.
  echo The photo manager exited with an error.
  pause
)
endlocal
