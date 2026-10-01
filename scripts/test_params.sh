#!/bin/sh
# Проверка всех параметров командной строки эмулятора.
# Каждое окно эмулятора нужно закрыть, чтобы открылось следующее.
cd "$(dirname "$0")/.." || exit 1

echo "1. Без параметров"
python3 src/main.py

echo "2. Только путь к VFS"
python3 src/main.py --vfs vfs

echo "3. Только стартовый скрипт"
python3 src/main.py --script scripts/start.txt

echo "4. Оба параметра"
python3 src/main.py --vfs vfs --script scripts/start.txt

echo "5. Скрипт с exit (окно закроется само)"
python3 src/main.py --script scripts/exit.txt
