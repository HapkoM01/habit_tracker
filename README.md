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

## 👨‍💻 Код написал:

### 𝑯𝒂𝒑𝒌𝒐𝑴 - 𝑩𝒆𝒈𝒊𝒏𝒏𝒆𝒓 𝑷𝒚𝒕𝒉𝒐𝒏-𝒅𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓!