"""
Telegram-бот для Habit Tracker (long polling).

Команды:
  /start <email>  — привязка аккаунта
  /help           — справка
  /habits         — список своих привычек
  /done <id>      — отметить привычку выполненной (сегодня)

Запуск: python manage.py run_telegram_bot
"""
import logging
import time
from datetime import date

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)

HELP_TEXT = (
    '📋 Команды бота Habit Tracker:\n\n'
    '/start your@email.com — привязать аккаунт\n'
    '/habits — список ваших привычек\n'
    '/done <id> — отметить привычку выполненной\n'
    '/help — эта справка\n\n'
    'Напоминания приходят автоматически по расписанию.'
)


class Command(BaseCommand):
    help = 'Запуск Telegram-бота (long polling)'

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token or token == 'replace_me':
            self.stderr.write('Укажите TELEGRAM_BOT_TOKEN в .env')
            return

        self.api = f'https://api.telegram.org/bot{token}'
        self._register_commands()
        offset = None
        self.stdout.write(self.style.SUCCESS('Bot started. Commands: /start /help /habits /done'))

        while True:
            try:
                params = {'timeout': 30}
                if offset:
                    params['offset'] = offset
                resp = requests.get(f'{self.api}/getUpdates', params=params, timeout=35)
                data = resp.json()
                if not data.get('ok'):
                    time.sleep(3)
                    continue
                for update in data.get('result', []):
                    offset = update['update_id'] + 1
                    self._handle_update(update)
            except Exception as exc:
                logger.exception('Bot loop error: %s', exc)
                time.sleep(5)

    def _register_commands(self):
        """Меню команд в Telegram."""
        commands = [
            {'command': 'start', 'description': 'Привязать аккаунт: /start email'},
            {'command': 'help', 'description': 'Справка по командам'},
            {'command': 'habits', 'description': 'Список моих привычек'},
            {'command': 'done', 'description': 'Отметить выполнение: /done <id>'},
        ]
        try:
            requests.post(
                f'{self.api}/setMyCommands',
                json={'commands': commands},
                timeout=10,
            )
        except requests.RequestException:
            pass

    def _handle_update(self, update):
        message = update.get('message') or {}
        text = (message.get('text') or '').strip()
        chat = message.get('chat') or {}
        chat_id = str(chat.get('id', ''))
        if not text or not chat_id:
            return

        # убрать @botname из команды
        if ' ' in text:
            cmd, arg = text.split(maxsplit=1)
        else:
            cmd, arg = text, ''
        cmd = cmd.split('@')[0].lower()

        if cmd == '/start':
            self._cmd_start(chat_id, chat, arg)
        elif cmd == '/help':
            self._send(chat_id, HELP_TEXT)
        elif cmd == '/habits':
            self._cmd_habits(chat_id)
        elif cmd == '/done':
            self._cmd_done(chat_id, arg)
        else:
            self._send(chat_id, 'Неизвестная команда.\n\n' + HELP_TEXT)

    def _cmd_start(self, chat_id, chat, email):
        email = email.strip()
        if not email:
            self._send(
                chat_id,
                'Чтобы получать напоминания, привяжите аккаунт:\n'
                '/start your@email.com\n\n' + HELP_TEXT,
            )
            return
        try:
            user = User.objects.get(email=email)
            user.telegram_id = chat_id
            user.telegram_username = chat.get('username')
            user.save(update_fields=['telegram_id', 'telegram_username'])
            self._send(
                chat_id,
                f'✅ Привязка успешна!\nEmail: {email}\n\n'
                f'Напоминания будут приходить в этот чат.\n'
                f'Список привычек: /habits',
            )
        except User.DoesNotExist:
            self._send(
                chat_id,
                f'❌ Пользователь {email} не найден.\n'
                f'Сначала зарегистрируйтесь: POST /api/auth/register/',
            )

    def _cmd_habits(self, chat_id):
        user = self._user_by_chat(chat_id)
        if not user:
            return
        from habits.models import Habit

        habits = Habit.objects.filter(user=user).order_by('time')
        if not habits.exists():
            self._send(chat_id, 'У вас пока нет привычек. Создайте их через API /api/habits/')
            return

        lines = ['📝 Ваши привычки:\n']
        for h in habits:
            kind = '😊 приятная' if h.is_pleasant else '💪 полезная'
            reward = f' → {h.reward}' if h.reward else ''
            related = f' → +{h.related_habit.action}' if h.related_habit_id else ''
            lines.append(
                f'#{h.id} {h.time.strftime("%H:%M")} — {h.action}\n'
                f'   📍 {h.place} | {kind} | раз в {h.periodicity} дн.{reward}{related}\n'
            )
        lines.append('\nОтметить выполнение: /done <id>')
        self._send(chat_id, '\n'.join(lines))

    def _cmd_done(self, chat_id, arg):
        user = self._user_by_chat(chat_id)
        if not user:
            return
        from habits.models import Habit, HabitLog

        try:
            habit_id = int(arg.strip())
        except (ValueError, AttributeError):
            self._send(chat_id, 'Использование: /done <id>\nСписок id: /habits')
            return

        try:
            habit = Habit.objects.get(pk=habit_id, user=user)
        except Habit.DoesNotExist:
            self._send(chat_id, f'Привычка #{habit_id} не найдена среди ваших.')
            return

        today = timezone.localdate()
        log, created = HabitLog.objects.get_or_create(
            habit=habit,
            date=today,
            defaults={'completed': True},
        )
        if not created and log.completed:
            self._send(chat_id, f'ℹ️ «{habit.action}» уже отмечена на сегодня.')
            return

        log.completed = True
        log.save(update_fields=['completed'])
        msg = f'✅ Готово! «{habit.action}» выполнена ({today.strftime("%d.%m.%Y")}).'
        if habit.reward:
            msg += f'\n🎁 Вознаграждение: {habit.reward}'
        if habit.related_habit_id:
            msg += f'\n😊 Приятная привычка: {habit.related_habit.action}'
        self._send(chat_id, msg)

    def _user_by_chat(self, chat_id):
        try:
            return User.objects.get(telegram_id=chat_id)
        except User.DoesNotExist:
            self._send(
                chat_id,
                'Сначала привяжите аккаунт:\n/start your@email.com',
            )
            return None

    def _send(self, chat_id, text):
        try:
            requests.post(
                f'{self.api}/sendMessage',
                json={'chat_id': chat_id, 'text': text},
                timeout=10,
            )
        except requests.RequestException as exc:
            logger.error('Send failed: %s', exc)
