#!/bin/bash
# Скрипт первичной настройки Ubuntu-сервера (запускать один раз по SSH)
set -e

PROJECT_DIR="${HOME}/habit_tracker"
REPO_URL="${1:-}"

echo "=== Обновление системы ==="
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx redis-server git

echo "=== Redis ==="
sudo systemctl enable redis-server
sudo systemctl start redis-server

if [ -n "$REPO_URL" ]; then
  echo "=== Клонирование репозитория ==="
  git clone "$REPO_URL" "$PROJECT_DIR" || true
fi

cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Заполните $PROJECT_DIR/.env перед продолжением!"
fi

mkdir -p data staticfiles media
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "=== Systemd ==="
sudo cp deploy/habit_tracker.service /etc/systemd/system/
sudo cp deploy/celery.service /etc/systemd/system/
sudo cp deploy/celery-beat.service /etc/systemd/system/
# поправьте пути User/WorkingDirectory под своего пользователя
sudo systemctl daemon-reload
sudo systemctl enable habit_tracker celery celery-beat
sudo systemctl start habit_tracker celery celery-beat

echo "=== Nginx ==="
sudo cp deploy/nginx.conf /etc/nginx/sites-available/habit_tracker
sudo sed -i "s|YOUR_SERVER_IP_OR_DOMAIN|$(curl -s ifconfig.me || echo '_')|g" /etc/nginx/sites-available/habit_tracker
sudo sed -i "s|/home/ubuntu/habit_tracker|$PROJECT_DIR|g" /etc/nginx/sites-available/habit_tracker
sudo ln -sf /etc/nginx/sites-available/habit_tracker /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

echo "=== Firewall ==="
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "Готово. API: http://$(curl -s ifconfig.me)/api/docs/"
