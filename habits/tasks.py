import logging
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_habit_reminders():
    """
    Периодическая задача: ищет привычки, у которых сейчас время
    (с учётом periodicity), и шлёт напоминание в Telegram.
    """
    from habits.models import Habit

    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)
    # окно ±1 минута
    habits = Habit.objects.filter(
        is_pleasant=False,  # напоминаем о полезных
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        user__telegram_id__isnull=False,
    ).exclude(user__telegram_id='').select_related('user', 'related_habit')

    sent = 0
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or token == 'replace_me':
        logger.warning('TELEGRAM_BOT_TOKEN not configured')
        return 'Telegram token not set'

    for habit in habits:
        # periodicity: отправляем каждые N дней от created_at
        days_since = (now.date() - habit.created_at.date()).days
        if days_since % habit.periodicity != 0:
            continue

        text = (
            f'⏰ Напоминание о привычке!\n\n'
            f'Действие: {habit.action}\n'
            f'Место: {habit.place}\n'
            f'Время: {habit.time.strftime("%H:%M")}\n'
            f'На выполнение: ~{habit.time_to_complete} сек.'
        )
        if habit.reward:
            text += f'\nВознаграждение: {habit.reward}'
        if habit.related_habit:
            text += f'\nПосле — приятная: {habit.related_habit.action}'

        chat_id = habit.user.telegram_id
        try:
            resp = requests.post(
                f'https://api.telegram.org/bot{token}/sendMessage',
                json={'chat_id': chat_id, 'text': text},
                timeout=10,
            )
            if resp.ok:
                sent += 1
            else:
                logger.error('Telegram API error: %s', resp.text)
        except requests.RequestException as exc:
            logger.error('Telegram request failed: %s', exc)

    return f'Sent {sent} reminders'


@shared_task
def send_telegram_message(chat_id: str, text: str):
    """Отправка одного сообщения в Telegram."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or token == 'replace_me':
        return 'Telegram token not set'
    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': text},
            timeout=10,
        )
        return resp.json()
    except requests.RequestException as exc:
        return str(exc)
