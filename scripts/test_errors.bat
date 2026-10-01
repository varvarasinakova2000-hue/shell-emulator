@echo off
rem Check handling of invalid command line parameters.
cd /d "%~dp0.."
set PY=python
where py >nul 2>nul && set PY=py

echo 1. Startup script does not exist
%PY% src\main.py --script scripts\not_found.txt

echo 2. Unknown parameter
%PY% src\main.py --unknown value

echo 3. Parameter without a value
%PY% src\main.py --vfs

echo 4. Help
%PY% src\main.py --help

pause
