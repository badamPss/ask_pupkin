#!/bin/bash

cd "$(dirname "$0")/../.."
source venv/bin/activate 2>/dev/null || true

echo "Запуск всех серверов для тестирования..."
echo ""

echo "1. Django Gunicorn (порт 8000) - для тестов 4, 5..."
gunicorn -c deploy/gunicorn/gunicorn_config.py > /dev/null 2>&1 &
sleep 1

echo "2. Static WSGI (порт 8001) - для теста 2..."
gunicorn -c deploy/gunicorn/gunicorn_static_config.py > /dev/null 2>&1 &
sleep 1

echo "3. Dynamic WSGI (порт 8002) - для теста 3..."
gunicorn -c deploy/gunicorn/gunicorn_dynamic_config.py > /dev/null 2>&1 &
sleep 1

echo ""
echo "✅ Все серверы запущены!"
echo ""
echo "Для остановки всех серверов: pkill -f gunicorn"

