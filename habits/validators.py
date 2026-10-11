"""Валидаторы для сериализаторов привычек."""
from rest_framework import serializers


def validate_time_to_complete(value):
    """Время выполнения не больше 120 секунд."""
    if value > 120:
        raise serializers.ValidationError(
            'Время выполнения не должно превышать 120 секунд.'
        )
    return value


def validate_periodicity(value):
    """Периодичность от 1 до 7 дней."""
    if value < 1:
        raise serializers.ValidationError(
            'Периодичность должна быть не менее 1 дня.'
        )
    if value > 7:
        raise serializers.ValidationError(
            'Нельзя выполнять привычку реже, чем 1 раз в 7 дней '
            '(periodicity ≤ 7).'
        )
    return value


def validate_related_or_reward(is_pleasant, related, reward):
    """
    Правила награды и связанной привычки.

    - нельзя указать оба сразу;
    - у приятной не может быть ни reward, ни related;
    - у полезной (is_pleasant=False) обязательно одно из двух.
    """
    has_related = related is not None
    has_reward = bool(reward and str(reward).strip())

    if has_related and has_reward:
        raise serializers.ValidationError(
            'Нельзя одновременно указать связанную привычку '
            'и вознаграждение.'
        )

    if is_pleasant:
        if has_reward:
            raise serializers.ValidationError({
                'reward': 'У приятной привычки не может быть вознаграждения.',
            })
        if has_related:
            raise serializers.ValidationError({
                'related_habit': (
                    'У приятной привычки не может быть связанной привычки.'
                ),
            })
    else:
        # полезная привычка — нужно reward ИЛИ related_habit
        if not has_related and not has_reward:
            raise serializers.ValidationError(
                'У полезной привычки должно быть заполнено '
                'вознаграждение (reward) или связанная привычка '
                '(related_habit).'
            )

    if has_related and not related.is_pleasant:
        raise serializers.ValidationError({
            'related_habit': 'Связанной может быть только приятная привычка.',
        })
