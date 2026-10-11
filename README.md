# Habit Tracker API

Трекер полезных привычек (Atomic Habits): Django + DRF + Celery + Telegram.

## Быстрый старт

```bash
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# заполните TELEGRAM_BOT_TOKEN, CELERY_BROKER_URL

python manage.py migrate
python manage.py createsuperuser  # email + password
python manage.py runserver
```

### Celery + Redis

```bash
# Redis должен быть запущен
celery -A config worker -l info --pool=solo   # Windows: --pool=solo
celery -A config beat -l info
```

### Telegram-бот

1. Создайте бота у [@BotFather](https://t.me/BotFather), токен → `.env`
2. Запуск: `python manage.py run_telegram_bot`
3. В Telegram: `/start your@email.com` — привязка chat_id

## API

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/token/` | JWT access/refresh |
| GET/PATCH | `/api/users/me/` | Профиль (telegram_id) |
| GET/POST | `/api/habits/` | Свои привычки (пагинация 5) |
| GET/PATCH/DELETE | `/api/habits/{id}/` | Одна привычка |
| GET | `/api/habits/public/` | Публичные привычки |

Документация: http://127.0.0.1:8000/api/docs/

## Валидаторы

- `time_to_complete` ≤ 120 сек
- `periodicity` от 1 до 7 дней
- нельзя одновременно `reward` и `related_habit`
- приятная привычка без reward/related
- `related_habit` только с `is_pleasant=True`

## Тесты

```bash
python manage.py test
coverage run --source='habits,users' manage.py test
coverage report -m
```


## Docker Compose

Запуск всех сервисов одной командой:

```bash
cp .env.example .env
# заполните SECRET_KEY и TELEGRAM_BOT_TOKEN

docker compose up --build -d
```

Сервисы:

| Сервис | Описание | Порты |
|--------|----------|-------|
| `web` | Django (gunicorn) | **8000** (expose + ports) |
| `redis` | брокер Celery | только внутри сети (volume `redis_data`) |
| `celery` | worker | — |
| `celery-beat` | периодические задачи | — |

Данные сохраняются в volumes: `redis_data`, `sqlite_data`.

API: http://localhost:8000/api/docs/

Остановка:

```bash
docker compose down
```

Логи:

```bash
docker compose logs -f web
docker compose logs -f celery
```


## Деплой на сервер (Gunicorn + Nginx)

### 1. Подготовка сервера (Ubuntu)

```bash
# на сервере
sudo apt update && sudo apt install -y python3-venv nginx redis-server git
git clone <URL_РЕПОЗИТОРИЯ> ~/habit_tracker
cd ~/habit_tracker
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt gunicorn
cp .env.example .env   # заполнить SECRET_KEY, ALLOWED_HOSTS, TELEGRAM_BOT_TOKEN
mkdir -p data staticfiles
python manage.py migrate
python manage.py collectstatic --noinput
```

Или одним скриптом: `bash deploy/setup_server.sh <URL_РЕПО>`

### 2. Systemd (авто-перезапуск)

```bash
sudo cp deploy/habit_tracker.service /etc/systemd/system/
sudo cp deploy/celery.service /etc/systemd/system/
sudo cp deploy/celery-beat.service /etc/systemd/system/
# отредактируйте User и пути под себя
sudo systemctl daemon-reload
sudo systemctl enable --now habit_tracker celery celery-beat
```

### 3. Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/habit_tracker
# укажите server_name (IP или домен)
sudo ln -s /etc/nginx/sites-available/habit_tracker /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo ufw allow OpenSSH && sudo ufw allow 'Nginx Full' && sudo ufw enable
```

Gunicorn слушает только `127.0.0.1:8000`, наружу — порт 80 через Nginx.

### 4. GitHub Actions Secrets

В репозитории → Settings → Secrets and variables → Actions:

| Secret | Значение |
|--------|----------|
| `SERVER_HOST` | IP сервера |
| `SERVER_USER` | `ubuntu` (или ваш) |
| `SSH_PRIVATE_KEY` | приватный SSH-ключ (весь файл) |
| `SERVER_PORT` | `22` (опционально) |
| `PROJECT_PATH` | `/home/ubuntu/habit_tracker` |

SSH-ключ: на сервере `ssh-keygen -t ed25519`, публичный в `~/.ssh/authorized_keys`, приватный — в Secret.

Workflow: `.github/workflows/ci-cd.yml`  
этапы: **lint → tests → deploy** (деплой только после успешных тестов на push).

## 👨‍💻 Код написал:

### 𝑯𝒂𝒑𝒌𝒐𝑴 - 𝑩𝒆𝒈𝒊𝒏𝒏𝒆𝒓 𝑷𝒚𝒕𝒉𝒐𝒏-𝒅𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓!