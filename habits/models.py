from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Habit(models.Model):
    """
    Привычка: «я буду [действие] в [время] в [место]».
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь',
    )
    place = models.CharField(max_length=255, verbose_name='Место')
    time = models.TimeField(verbose_name='Время')
    action = models.CharField(max_length=255, verbose_name='Действие')
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка',
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_to',
        verbose_name='Связанная привычка',
        help_text='Только приятная привычка; нельзя одновременно с вознаграждением',
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Периодичность (дней)',
        help_text='Как часто выполнять: 1 — ежедневно. Не реже 1 раза в 7 дней.',
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Вознаграждение',
    )
    time_to_complete = models.PositiveSmallIntegerField(
        default=60,
        verbose_name='Время на выполнение (сек)',
        help_text='Не более 120 секунд',
    )
    is_public = models.BooleanField(default=False, verbose_name='Публичная')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} @ {self.time} ({self.place})'

    def clean(self):
        errors = {}

        if self.time_to_complete and self.time_to_complete > 120:
            errors['time_to_complete'] = (
                'Время выполнения не должно превышать 120 секунд.'
            )

        if self.periodicity is not None and self.periodicity > 7:
            errors['periodicity'] = (
                'Нельзя выполнять привычку реже, чем 1 раз в 7 дней '
                '(periodicity ≤ 7).'
            )
        if self.periodicity is not None and self.periodicity < 1:
            errors['periodicity'] = (
                'Периодичность должна быть не менее 1 дня.'
            )

        has_related = self.related_habit is not None
        has_reward = bool(self.reward and str(self.reward).strip())

        if has_related and has_reward:
            msg = (
                'Нельзя одновременно указать связанную привычку '
                'и вознаграждение.'
            )
            errors['reward'] = msg
            errors['related_habit'] = msg

        if self.is_pleasant:
            if has_reward:
                errors['reward'] = (
                    'У приятной привычки не может быть вознаграждения.'
                )
            if has_related:
                errors['related_habit'] = (
                    'У приятной привычки не может быть связанной привычки.'
                )
        else:
            if not has_related and not has_reward:
                errors['reward'] = (
                    'У полезной привычки должно быть заполнено '
                    'вознаграждение или связанная привычка.'
                )

        if has_related and not self.related_habit.is_pleasant:
            errors['related_habit'] = (
                'Связанной может быть только приятная привычка.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class HabitLog(models.Model):
    """Отметка о выполнении привычки за день."""
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Привычка',
    )
    date = models.DateField(verbose_name='Дата')
    completed = models.BooleanField(default=True, verbose_name='Выполнена')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Выполнение'
        verbose_name_plural = 'Выполнения'
        unique_together = ('habit', 'date')
        ordering = ['-date']

    def __str__(self):
        status = '✓' if self.completed else '✗'
        return f'{status} {self.habit} — {self.date}'
