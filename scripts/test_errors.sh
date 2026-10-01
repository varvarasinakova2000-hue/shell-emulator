#!/bin/sh
# Проверка обработки ошибочных параметров командной строки.
cd "$(dirname "$0")/.." || exit 1

echo "1. Несуществующий стартовый скрипт"
python3 src/main.py --script scripts/not_found.txt

echo "2. Неизвестный параметр"
python3 src/main.py --unknown value

echo "3. Параметр без значения"
python3 src/main.py --vfs

echo "4. Справка по параметрам"
python3 src/main.py --help
