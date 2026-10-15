# CodeHub — команды разработчика
.PHONY: help install migrate seed run test check superuser fresh clean

help:
	@echo "CodeHub — доступные команды:"
	@echo "  make install    создать .venv и установить зависимости"
	@echo "  make migrate    применить миграции (создаёт контент сайта)"
	@echo "  make seed       демо-данные: преподаватель, студент, задания"
	@echo "  make run        запустить сервер (порт 8080)"
	@echo "  make test       запустить тесты"
	@echo "  make check      системные проверки Django"
	@echo "  make superuser  создать администратора"
	@echo "  make fresh      пересоздать базу с нуля"
	@echo "  make clean      удалить кэши и временные файлы"

install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

migrate:
	.venv/bin/python manage.py migrate

seed:
	.venv/bin/python manage.py seed_codehub --with-demo-work

run:
	./run_local.sh

test:
	.venv/bin/python manage.py test

check:
	.venv/bin/python manage.py check

superuser:
	.venv/bin/python manage.py createsuperuser

fresh:
	rm -f db.sqlite3
	.venv/bin/python manage.py migrate
	.venv/bin/python manage.py seed_codehub --with-demo-work

clean:
	find . -type d -name '__pycache__' -not -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -not -path './.venv/*' -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache
