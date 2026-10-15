#!/usr/bin/env bash
# ==========================================================================
# Локальный запуск CodeHub (в том числе с доступом через ngrok).
#
#   ./run_local.sh                 # порт 8080 (совпадает с ngrok-туннелем)
#   PORT=8000 ./run_local.sh       # другой порт
#   NGROK_HOST=example.ngrok-free.dev ./run_local.sh
# ==========================================================================
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Виртуальное окружение .venv не найдено. Создайте его: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

PORT="${PORT:-8080}"
NGROK_HOST="${NGROK_HOST:-issue-boogieman-aging.ngrok-free.dev}"

# Доступ по локальной сети и через ngrok: разрешаем оба имени.
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0,[::1],${NGROK_HOST}"
# ngrok работает по HTTPS, поэтому origin нужно явно добавить в доверенные (CSRF).
export DJANGO_CSRF_TRUSTED_ORIGINS="https://${NGROK_HOST}"

python manage.py migrate --noinput >/dev/null

echo "---------------------------------------------------------------"
echo "  Локально:  http://127.0.0.1:${PORT}/"
echo "  ngrok:     https://${NGROK_HOST}/"
echo "  Админка:   http://127.0.0.1:${PORT}/admin/"
echo "  Остановить: Ctrl+C"
echo "---------------------------------------------------------------"

exec python manage.py runserver "0.0.0.0:${PORT}"
