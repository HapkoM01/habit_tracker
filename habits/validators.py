"""Валидаторы для сериализаторов привычек."""
from rest_framework import serializers


def validate_time_to_complete(value):
    if value > 120:
        raise serializers.ValidationError(
            'Время выполнения не должно превышать 120 секунд.'
        )
    return value


def validate_periodicity(value):
    if value < 1:
        raise serializers.ValidationError('Периодичность должна быть не менее 1 дня.')
    if value > 7:
        raise serializers.ValidationError(
            'Нельзя выполнять привычку реже, чем 1 раз в 7 дней (periodicity ≤ 7).'
        )
    return value
