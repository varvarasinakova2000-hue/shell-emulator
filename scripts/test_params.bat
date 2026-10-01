@echo off
rem Run the emulator with every combination of command line parameters.
rem Close each emulator window to start the next run.
cd /d "%~dp0.."
set PY=python
where py >nul 2>nul && set PY=py

echo 1. No parameters
%PY% src\main.py

echo 2. VFS path only
%PY% src\main.py --vfs vfs

echo 3. Startup script only
%PY% src\main.py --script scripts\start.txt

echo 4. Both parameters
%PY% src\main.py --vfs vfs --script scripts\start.txt

echo 5. Script with exit (the window closes by itself)
%PY% src\main.py --script scripts\exit.txt

pause
