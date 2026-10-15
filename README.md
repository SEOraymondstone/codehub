# CodeHub

Веб-платформа для онлайн-курса программирования: публичный одностраничный сайт-визитка
и закрытый личный кабинет для сдачи и проверки домашних заданий.

## Оформление: два интерфейса — две темы

| Интерфейс | Аудитория | Стиль |
|-----------|-----------|-------|
| **Публичный лендинг** (`/`) | родители и новые ученики | мягкая светлая палитра, крупные читаемые шрифты, спокойный зелёный акцент, карточки и понятная навигация |
| **Личный кабинет** (`/dashboard/`, `/homework/`, `/accounts/`) | студенты и преподаватель | терминальный стиль: чёрный фон и кислотно-зелёные акценты |

Темы полностью независимы: публичный лендинг использует
[`templates/base.html`](templates/base.html) + [`static/css/public.css`](static/css/public.css),
а закрытая платформа — [`templates/base_cabinet.html`](templates/base_cabinet.html) +
[`static/css/style.css`](static/css/style.css). Вёрстка адаптивна и корректно работает
на ПК, планшетах и телефонах.

## Контент без кода («под ключ»)

Весь текст и цифры публичного сайта хранятся в базе и правятся в админке
(`/admin/`), менять код для этого не нужно:

| Раздел админки | Что редактируется |
|---|---|
| **Настройки сайта** | название, слоган, заголовок и подзаголовок первого экрана, цена «от», телефоны, email, соцсети |
| **Цифры на первом экране** | «6 модулей», «24/7», «1:1» и любые другие |
| **Преимущества** | карточки «Почему родители выбирают нас» |
| **Тарифы** | названия, цены, списки «что входит», выделенный тариф |
| **Преподаватели** | имя, должность, биография, фото |
| **Отзывы** | автор, кто он, текст отзыва |
| **Частые вопросы** | вопрос и ответ |
| **Заявки / Сообщения / Модули курса** | заявки с лендинга, письма, программа обучения |

У каждого блока есть порядок вывода и флаг «Опубликовано». Если блок отключён
или пуст — соответствующий раздел на сайте просто не показывается, никакого
захардкоженного текста не остаётся.

---

## 1. Возможности

### Публичная часть — для родителей
- **Лендинг `/`** — мягкая светлая тема и «захватывающие» детали: анимированный
  фон первого экрана, живые цифры, бегущая строка технологий, окно с кодом
  (эффект печатной машинки), карточка преподавателя, отзывы, тарифы и FAQ.
  Весь контент берётся из базы и правится в админке.
- **Страница ознакомления `/guide/`** — пошаговая инструкция «Как учиться»
  в **тёмной** теме: заявка → кабинет → сдача ДЗ → проверка → обратная связь → доработка,
  плюс блоки «Родителям» и «Что понадобится».
- **Политика конфиденциальности `/privacy/`** — обязательная для доверия страница
  об обработке персональных данных, ссылка есть в футере.
- **SEO-основа**: `robots.txt`, `sitemap.xml`, canonical, Open Graph и разметка
  Schema.org (`Course` + `Offer`), чтобы курс солидно выглядел и в поиске.
- Hero-секция с названием проекта, описанием курса и стоимостью «от 100 $».
- Программа курса, собираемая из модулей в базе данных.
- Блоки «формат обучения», тарифы и призывы к действию.
- Контакты: два телефона, email, ссылки на Telegram, WhatsApp, Instagram, YouTube, GitHub.
- Две формы захвата контактов (под таргетированную рекламу):
  - заявка на консультацию в первом экране (модель `Lead`);
  - сообщение через блок контактов (модель `ContactMessage`).
- Поддержка UTM-меток (`utm_source`, `utm_campaign` сохраняются в заявке) и honeypot-защита от спама.
- Health-check `/healthz/` для мониторинга.

### Личный кабинет (закрытая часть)
- Регистрация и авторизация, роли **Студент** и **Преподаватель/Администратор**.
- **Студент**:
  - блок **«Что дальше»**, который подсказывает следующий шаг (сдать / доработать / ждать проверки);
  - список домашних заданий в виде карточек с понятными действиями и прогрессом курса;
  - загрузка файла с решением (архивы, код, документы, изображения; до 20 МБ) и повторная отправка;
  - просмотр балла и письменной обратной связи преподавателя прямо в списке;
  - **двусторонняя переписка** с преподавателем по каждой работе;
  - индикатор новых сообщений от преподавателя.
- **Преподаватель**:
  - блок **«Очередь проверки»** и кнопка **«Сохранить и проверить следующую»** —
    проверка потока работ без возврата в список;
  - список всех работ с фильтрами по статусу, заданию, поиском и быстрым пресетом «Ждут проверки»;
  - просмотр и скачивание работы, выставление балла и обратной связи;
  - управление статусами («Проверено», «На доработку» и т. д.);
  - **двусторонняя переписка** со студентом на странице проверки;
  - индикатор вопросов студентов без ответа;
  - создание и редактирование домашних заданий;
  - уведомления на email о новых работах, сообщениях и результатах проверки (настраиваются).
- Обе роли: адаптивная вёрстка — таблицы автоматически превращаются в карточки на телефонах.
- Встроенная защищённая административная панель Django (`/admin/`) с управлением
  пользователями, модулями курса, заявками и работами.

---

## 2. Технологии

| Слой | Технология |
|------|------------|
| Бэкенд | Python 3.12+, Django 6.1 |
| База данных | SQLite (по умолчанию) / PostgreSQL (production) |
| Файлы | Локальное файловое хранилище `media/` |
| Статика | WhiteNoise + сжатый hashed-манифест |
| WSGI | Gunicorn |
| Фронтенд | Django-шаблоны, чистый CSS и немного vanilla JS (без сборщиков) |

---

## 3. Структура проекта

```
.
├── codehub/            # настройки, корневые URL, WSGI/ASGI
├── accounts/           # кастомная модель User с ролями, регистрация, профиль
├── courses/            # модули программы курса и заявки (Lead)
├── homework/           # задания, работы студентов, проверки и оценки
├── dashboard/          # личный кабинет (роутинг по ролям, сводки)
├── pages/              # публичный лендинг, контактные сообщения, health-check
├── templates/          # base.html (публичный) + base_cabinet.html (кабинет)
│   ├── pages/          # лендинг
│   ├── accounts/       # вход, регистрация, профиль
│   ├── dashboard/      # кабинеты студента и преподавателя
│   └── homework/       # задания, работы, проверки
├── static/             # css/public.css, css/style.css (кабинет), js/app.js
├── deploy/             # gunicorn.service, nginx.conf, deploy.sh, entrypoint.sh
├── run_local.sh        # локальный запуск (+ настройка хостов для ngrok)
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## 4. Быстрый старт (локально)

```bash
# 1. Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# 2. Зависимости
pip install -r requirements.txt

# 3. Переменные окружения (для локальной разработки достаточно значений по умолчанию)
cp .env.example .env

# 4. База данных
python manage.py migrate

# 5. Демо-данные: модули курса, преподаватель, студент, задания
python manage.py seed_codehub --with-demo-work

# 6. Администратор
python manage.py createsuperuser

# 7. Запуск (порт 8080 — совпадает с ngrok-туннелем)
./run_local.sh
```

Сайт: <http://127.0.0.1:8080/> · Админка: <http://127.0.0.1:8080/admin/>

Скрипт [`run_local.sh`](run_local.sh) активирует окружение, применяет миграции и
подставляет `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` для ngrok. Порт и домен
переопределяются переменными:

```bash
PORT=8000 ./run_local.sh
NGROK_HOST=my-tunnel.ngrok-free.dev ./run_local.sh
```

### Доступ через ngrok

1. Запустите локальный сервер: `./run_local.sh` (порт **8080**).
2. В другом терминале поднимите туннель на тот же порт: `ngrok http 8080`.
3. Откройте выданный адрес `https://<name>.ngrok-free.dev`. На бесплатном тарифе
   ngrok один раз показывает страницу-предупреждение — нажмите «Visit Site».
4. Если домен туннеля другой, передайте его в `NGROK_HOST`, чтобы Django принял
   хост и CSRF-запросы.

> Туннель должен указывать на тот же порт, на котором запущен `run_local.sh`
> (по умолчанию 8080). Если адрес в панели ngrok другой — запустите
> `PORT=<порт> ./run_local.sh`.

### Демо-доступы после `seed_codehub`

| Роль | Логин | Пароль |
|------|-------|--------|
| Преподаватель | `teacher` | `teacher12345` |
| Студент | `student` | `student12345` |

> **Важно:** смените эти пароли перед публикацией в интернет.

---

## 5. Переменные окружения

Все настройки читаются из переменных окружения (см. `.env.example`).

| Переменная | Назначение | По умолчанию |
|------------|-----------|--------------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django | небезопасный dev-ключ |
| `DJANGO_DEBUG` | Режим отладки | `true` |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты (через запятую) | `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Доверенные origin'ы для CSRF | пусто |
| `DATABASE_URL` | Строка подключения, например `postgres://user:pass@host:5432/db` | SQLite |
| `POSTGRES_DB`/`POSTGRES_USER`/… | Альтернатива `DATABASE_URL` | — |
| `DJANGO_EMAIL_BACKEND` | Бэкенд почты | консольный |
| `EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`/`EMAIL_USE_TLS` | SMTP | — |
| `TEACHER_NOTIFICATION_EMAIL` | Кому слать уведомления о новых работах | пусто |
| `CODEHUB_*` | Название, слоган, цена, телефоны, соцсети на лендинге | значения из settings |
| `HOMEWORK_MAX_UPLOAD_SIZE` | Максимальный размер файла ДЗ, байт | 1 ГБ |
| `DJANGO_SECURE_SSL_REDIRECT` | Редирект HTTP → HTTPS | `true` в проде |
| `DJANGO_USE_MANIFEST_STATIC` | Hashed-манифест статики | `true` в проде |

---

## 6. Основные маршруты

| URL | Доступ | Описание |
|-----|--------|----------|
| `/` | все | лендинг с формами заявок |
| `/guide/` | все | страница ознакомления «Как учиться» |
| `/privacy/` | все | политика конфиденциальности |
| `/robots.txt` · `/sitemap.xml` | все | SEO: правила обхода и карта сайта |
| `/healthz/` | все | health-check |
| `/accounts/register/` | гости | регистрация студента |
| `/accounts/login/` · `/accounts/logout/` | все | вход и выход |
| `/accounts/profile/` | авторизованные | профиль |
| `/dashboard/` | авторизованные | редирект в кабинет по роли |
| `/dashboard/student/` | студент | сводка и прогресс |
| `/dashboard/teacher/` | преподаватель | список работ и фильтры |
| `/homework/` | студент | список заданий |
| `/homework/assignment/<id>/` | студент | карточка задания и загрузка файла |
| `/homework/teacher/submissions/<id>/` | преподаватель | проверка работы |
| `/homework/teacher/assignments/` | преподаватель | управление заданиями |
| `/admin/` | staff | административная панель |

---

## 7. Тесты

```bash
python manage.py test
```

Сейчас это **97 тестов**. Покрыты:

- роли и права доступа (403 для студента на страницах преподавателя, 404 для
  несуществующих объектов, редирект анонимных пользователей на вход);
- регистрация, вход/выход, редактирование профиля (две независимые формы не затирают
  данные друг друга);
- лендинг и формы заявок, включая honeypot и обязательный телефон;
- полный цикл «загрузка ДЗ → проверка → оценка», валидация балла и расширений файлов;
- **двусторонняя переписка**: ответы в обе стороны, запрет писать к чужой работе,
  экранирование HTML (защита от XSS), счётчики непрочитанных;
- очередь проверки и кнопка «Сохранить и проверить следующую»;
- защита файлов работ: прямая ссылка закрыта, чужой студент получает 403;
- граничные случаи входа (open redirect, неактивный пользователь, слабый пароль),
  CSRF, лимиты длины ввода, устойчивость фильтров и идемпотентность сидирования;
- health-check.

---

## 8. Деплой на удалённый сервер (Ubuntu 22.04/24.04)

### 8.1. Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-dev build-essential \
    postgresql postgresql-contrib nginx git curl
```

### 8.2. Пользователь и каталог

```bash
sudo adduser --system --group --home /srv/codehub codehub
sudo mkdir -p /srv/codehub/app
sudo chown -R codehub:codehub /srv/codehub
sudo -u codehub git clone <URL-репозитория> /srv/codehub/app
```

### 8.3. PostgreSQL

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE codehub;
CREATE USER codehub WITH ENCRYPTED PASSWORD 'strong-password';
ALTER ROLE codehub SET client_encoding TO 'utf8';
ALTER ROLE codehub SET default_transaction_isolation TO 'read committed';
ALTER ROLE codehub SET timezone TO 'Europe/Moscow';
GRANT ALL PRIVILEGES ON DATABASE codehub TO codehub;
ALTER DATABASE codehub OWNER TO codehub;
SQL
```

### 8.4. Приложение

```bash
cd /srv/codehub/app
sudo -u codehub python3 -m venv .venv
sudo -u codehub .venv/bin/pip install -r requirements.txt
sudo -u codehub cp .env.example .env
sudo -u codehub nano .env      # заполните ключи и доступы
sudo -u codehub .venv/bin/python manage.py migrate
sudo -u codehub .venv/bin/python manage.py collectstatic --noinput
sudo -u codehub .venv/bin/python manage.py createsuperuser
```

### 8.5. Gunicorn + systemd

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/codehub.service
sudo systemctl daemon-reload
sudo systemctl enable --now codehub
sudo systemctl status codehub
```

### 8.6. Nginx + HTTPS

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/codehub
sudo ln -s /etc/nginx/sites-available/codehub /etc/nginx/sites-enabled/codehub
sudo nginx -t && sudo systemctl reload nginx

# Бесплатный TLS-сертификат
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d codehub.example.com -d www.codehub.example.com
```

Не забудьте указать в `.env`:
```
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=codehub.example.com,www.codehub.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://codehub.example.com,https://www.codehub.example.com
DATABASE_URL=postgres://codehub:strong-password@127.0.0.1:5432/codehub
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### 8.7. Обновление версии

```bash
cd /srv/codehub/app
sudo -u codehub ./deploy/deploy.sh
```

### 8.8. Проверка конфигурации

```bash
DJANGO_DEBUG=false python manage.py check --deploy
```
Ожидается отсутствие ошибок, связанных с безопасностью и почтой
(используйте SMTP-бэкенд в проде).

---

## 9. Деплой через Docker

```bash
cp .env.example .env          # заполните переменные
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Сервисы: `db` (PostgreSQL 16) и `web` (Gunicorn). Каталоги `media` и `staticfiles`
хранятся в именованных томах. Приложение доступно на <http://localhost:8000/>.

---

## 10. Безопасность

- Пароли хранятся только в виде хешей (встроенная система Django).
- Все формы защищены CSRF-токеном.
- Загрузка файлов ограничена по расширению и размеру.
- **Файлы домашних работ не отдаются напрямую**: скачивание идёт через view
  с проверкой прав (автор работы или преподаватель), а прямой доступ к
  `/media/submissions/` закрыт — в dev средствами Django, в проде правилом nginx.
- Ролевая модель: студент не имеет доступа к кабинету преподавателя и чужим работам
  (проверяется декораторами `teacher_required` / `student_required`).
- В проде автоматически включаются: HSTS, secure-cookies, `X-Frame-Options: DENY`,
  `SECURE_CONTENT_TYPE_NOSNIFF`, редирект на HTTPS и `SECURE_PROXY_SSL_HEADER`.
- `DJANGO_SECRET_KEY` и доступы к БД задаются только через переменные окружения.

---

## 11. Лицензия

Проект создан по техническому заданию заказчика. Все права на контент курса
принадлежат владельцу CodeHub.
