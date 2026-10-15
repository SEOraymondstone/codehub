#!/usr/bin/env bash
# CodeHub — обновление приложения на сервере.
# Запускать из каталога проекта:  ./deploy/deploy.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/codehub/app}"
BRANCH="${BRANCH:-main}"
VENV="$APP_DIR/.venv"
PY="$VENV/bin/python"

echo "==> Переход в $APP_DIR"
cd "$APP_DIR"

echo "==> Получение обновлений из git ($BRANCH)"
git fetch --all
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "==> Обновление зависимостей"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -r requirements.txt

echo "==> Миграции"
"$PY" manage.py migrate --noinput

echo "==> Сбор статики"
"$PY" manage.py collectstatic --noinput

echo "==> Проверка конфигурации"
"$PY" manage.py check --deploy || true

echo "==> Перезапуск сервиса"
sudo systemctl restart codehub
sudo systemctl --no-pager status codehub | head -n 12

echo "==> Готово"
