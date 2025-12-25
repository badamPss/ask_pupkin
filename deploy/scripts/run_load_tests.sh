#!/bin/bash

echo "=========================================="
echo "Полное сравнение производительности"
echo "5 измерений согласно заданию"
echo "=========================================="
echo ""

BASE_DIR="/Users/ignatvaschilo/Downloads/ask_pupkin"
cd "$BASE_DIR"

if ! command -v ab &> /dev/null; then
    echo "❌ Apache Benchmark (ab) не установлен"
    echo "Установите: brew install httpd (на macOS)"
    exit 1
fi

RESULTS_FILE="$BASE_DIR/deploy/logs/performance_full_results.txt"
ANALYSIS_FILE="$BASE_DIR/deploy/logs/performance_analysis.txt"

mkdir -p "$(dirname "$RESULTS_FILE")"

echo "==========================================" > "$RESULTS_FILE"
echo "Результаты тестов производительности" >> "$RESULTS_FILE"
echo "Дата: $(date)" >> "$RESULTS_FILE"
echo "==========================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

extract_rps() {
    grep "Requests per second" | awk '{print $4}'
}

extract_time() {
    grep "Time per request" | head -1 | awk '{print $4}'
}

run_test() {
    local test_num=$1
    local name=$2
    local url=$3
    local description=$4
    
    echo ""
    echo "=========================================="
    echo "Тест $test_num: $name"
    echo "URL: $url"
    echo "Описание: $description"
    echo "=========================================="
    
    echo "" >> "$RESULTS_FILE"
    echo "Тест $test_num: $name" >> "$RESULTS_FILE"
    echo "URL: $url" >> "$RESULTS_FILE"
    echo "Описание: $description" >> "$RESULTS_FILE"
    echo "----------------------------------------" >> "$RESULTS_FILE"
    
    local output=$(ab -n 1000 -c 10 "$url" 2>&1)
    echo "$output" >> "$RESULTS_FILE"
    echo "$output"
    
    local rps=$(echo "$output" | extract_rps)
    local time=$(echo "$output" | extract_time)
    
    echo "Результат: $rps req/sec, $time ms/req" >> "$RESULTS_FILE"
    echo "$test_num|$name|$rps|$time" >> "$ANALYSIS_FILE"
}

rm -f "$ANALYSIS_FILE"
echo "test_num|name|rps|time_ms" > "$ANALYSIS_FILE"

echo "Тест 1: Статика через Nginx (прямой доступ)"
echo "----------------------------------------"
if lsof -i :80 2>/dev/null | grep -q LISTEN; then
    run_test "1" "Статика через Nginx" "http://localhost/sample.html" "Отдача статического документа напрямую через nginx"
else
    echo "⚠️  Nginx не запущен на порту 80"
    echo "Запустите: sudo nginx -c $BASE_DIR/deploy/nginx/nginx.conf"
fi

echo ""
echo "Тест 2: Статика через Gunicorn"
echo "----------------------------------------"
if lsof -i :8001 2>/dev/null | grep -q LISTEN; then
    run_test "2" "Статика через Gunicorn" "http://127.0.0.1:8001/sample.html" "Отдача статического документа напрямую через gunicorn"
else
    echo "⚠️  Static WSGI не запущен на порту 8001"
    echo "Запустите: ./deploy/scripts/start_static_wsgi.sh"
fi

echo ""
echo "Тест 3: Динамика через Gunicorn (прямой доступ)"
echo "----------------------------------------"
if lsof -i :8002 2>/dev/null | grep -q LISTEN; then
    run_test "3" "Динамика через Gunicorn" "http://127.0.0.1:8002/" "Отдача динамического документа напрямую через gunicorn"
else
    echo "⚠️  Dynamic WSGI не запущен на порту 8002"
    echo "Запустите: ./deploy/scripts/start_dynamic_wsgi.sh"
fi

echo ""
echo "Тест 4: Динамика через Nginx proxy (без кэша)"
echo "----------------------------------------"
if lsof -i :80 2>/dev/null | grep -q LISTEN && lsof -i :8000 2>/dev/null | grep -q LISTEN; then
    echo "⚠️  Для этого теста нужно временно отключить proxy_cache в nginx.conf"
    echo "Закомментируйте строки с proxy_cache в location /"
    echo "Затем перезапустите nginx и запустите тест вручную:"
    echo "  ab -n 1000 -c 10 http://localhost/ >> $RESULTS_FILE"
    echo ""
    echo "Или создайте копию nginx.conf без кэша для этого теста"
else
    echo "⚠️  Nginx или Django Gunicorn не запущены"
fi

echo ""
echo "Тест 5: Динамика через Nginx proxy (с кэшем)"
echo "----------------------------------------"
if lsof -i :80 2>/dev/null | grep -q LISTEN && lsof -i :8000 2>/dev/null | grep -q LISTEN; then
    echo "Прогрев кэша (первый запрос)..."
    curl -s http://localhost/ > /dev/null
    sleep 1
    run_test "5" "Динамика через Nginx proxy (с кэшем)" "http://localhost/" "Отдача динамического документа через проксирование запроса с nginx на gunicorn, при кэшировании ответа на nginx"
else
    echo "⚠️  Nginx или Django Gunicorn не запущены"
fi

echo ""
echo "=========================================="
echo "Анализ результатов"
echo "=========================================="
echo ""

if [ -f "$ANALYSIS_FILE" ] && [ $(wc -l < "$ANALYSIS_FILE") -gt 1 ]; then
    echo "Создаю анализ результатов..."
    
    python3 << 'PYTHON_SCRIPT'
import sys
import os

analysis_file = sys.argv[1]
results_file = sys.argv[2]

if not os.path.exists(analysis_file) or os.path.getsize(analysis_file) < 50:
    print("Недостаточно данных для анализа")
    sys.exit(0)

results = {}
with open(analysis_file, 'r') as f:
    lines = f.readlines()[1:]  # Skip header
    for line in lines:
        parts = line.strip().split('|')
        if len(parts) >= 4:
            test_num, name, rps, time = parts[0], parts[1], parts[2], parts[3]
            if rps and rps != 'None':
                results[test_num] = {
                    'name': name,
                    'rps': float(rps),
                    'time': float(time) if time and time != 'None' else 0
                }

print("\n" + "="*60)
print("АНАЛИЗ РЕЗУЛЬТАТОВ")
print("="*60)

if '1' in results and '2' in results:
    static_nginx = results['1']['rps']
    static_gunicorn = results['2']['rps']
    ratio = static_nginx / static_gunicorn if static_gunicorn > 0 else 0
    print(f"\n1. Сравнение статики:")
    print(f"   Nginx:        {static_nginx:.2f} req/sec")
    print(f"   Gunicorn:     {static_gunicorn:.2f} req/sec")
    print(f"   Nginx быстрее в {ratio:.2f} раз(а)")

if '3' in results and '2' in results:
    dynamic = results['3']['rps']
    static = results['2']['rps']
    ratio = static / dynamic if dynamic > 0 else 0
    print(f"\n2. Статика vs Динамика (через Gunicorn):")
    print(f"   Статика:      {static:.2f} req/sec")
    print(f"   Динамика:     {dynamic:.2f} req/sec")
    print(f"   Статика быстрее в {ratio:.2f} раз(а)")

if '4' in results and '5' in results:
    no_cache = results['4']['rps']
    with_cache = results['5']['rps']
    ratio = with_cache / no_cache if no_cache > 0 else 0
    print(f"\n3. Влияние proxy_cache:")
    print(f"   Без кэша:     {no_cache:.2f} req/sec")
    print(f"   С кэшем:      {with_cache:.2f} req/sec")
    print(f"   Кэш ускоряет в {ratio:.2f} раз(а)")

if '3' in results and '5' in results:
    direct = results['3']['rps']
    cached = results['5']['rps']
    ratio = cached / direct if direct > 0 else 0
    print(f"\n4. Динамика: прямой доступ vs Nginx proxy с кэшем:")
    print(f"   Прямой:       {direct:.2f} req/sec")
    print(f"   Proxy+кэш:    {cached:.2f} req/sec")
    print(f"   Proxy+кэш быстрее в {ratio:.2f} раз(а)")

print("\n" + "="*60)
print("ОТВЕТЫ НА ВОПРОСЫ:")
print("="*60)

if '1' in results and '2' in results:
    static_nginx = results['1']['rps']
    static_gunicorn = results['2']['rps']
    ratio = static_nginx / static_gunicorn if static_gunicorn > 0 else 0
    print(f"\nQ: Насколько быстрее отдается статика по сравнению с WSGI?")
    print(f"A: Статика через Nginx быстрее WSGI в {ratio:.2f} раз(а)")

if '4' in results and '5' in results:
    no_cache = results['4']['rps']
    with_cache = results['5']['rps']
    ratio = with_cache / no_cache if no_cache > 0 else 0
    print(f"\nQ: Во сколько раз ускоряет работу proxy_cache?")
    print(f"A: proxy_cache ускоряет работу в {ratio:.2f} раз(а)")

print("\n" + "="*60)
PYTHON_SCRIPT
    "$ANALYSIS_FILE" "$RESULTS_FILE"
    
    echo "" >> "$RESULTS_FILE"
    echo "==========================================" >> "$RESULTS_FILE"
    echo "Анализ результатов" >> "$RESULTS_FILE"
    echo "==========================================" >> "$RESULTS_FILE"
    python3 << 'PYTHON_SCRIPT'
import sys
import os

analysis_file = sys.argv[1]

if not os.path.exists(analysis_file) or os.path.getsize(analysis_file) < 50:
    sys.exit(0)

results = {}
with open(analysis_file, 'r') as f:
    lines = f.readlines()[1:]
    for line in lines:
        parts = line.strip().split('|')
        if len(parts) >= 4:
            test_num, name, rps, time = parts[0], parts[1], parts[2], parts[3]
            if rps and rps != 'None':
                results[test_num] = {
                    'name': name,
                    'rps': float(rps),
                    'time': float(time) if time and time != 'None' else 0
                }

with open(sys.argv[2], 'a') as f:
    if '1' in results and '2' in results:
        static_nginx = results['1']['rps']
        static_gunicorn = results['2']['rps']
        ratio = static_nginx / static_gunicorn if static_gunicorn > 0 else 0
        f.write(f"\n1. Статика: Nginx быстрее Gunicorn в {ratio:.2f} раз(а)\n")
    
    if '4' in results and '5' in results:
        no_cache = results['4']['rps']
        with_cache = results['5']['rps']
        ratio = with_cache / no_cache if no_cache > 0 else 0
        f.write(f"2. proxy_cache ускоряет в {ratio:.2f} раз(а)\n")
PYTHON_SCRIPT
    "$ANALYSIS_FILE" "$RESULTS_FILE"
fi

echo ""
echo "=========================================="
echo "Тесты завершены!"
echo "=========================================="
echo ""
echo "Полные результаты: $RESULTS_FILE"
echo "Анализ: $ANALYSIS_FILE"
echo ""
echo "Для просмотра результатов:"
echo "  cat $RESULTS_FILE"
echo "  cat $ANALYSIS_FILE"

