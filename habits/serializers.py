from rest_framework import serializers

from .models import Habit
from .validators import (
    validate_periodicity,
    validate_related_or_reward,
    validate_time_to_complete,
)


class HabitSerializer(serializers.ModelSerializer):
    time_to_complete = serializers.IntegerField(
        validators=[validate_time_to_complete],
    )
    periodicity = serializers.IntegerField(
        validators=[validate_periodicity],
        default=1,
    )

    class Meta:
        model = Habit
        fields = (
            'id',
            'user',
            'place',
            'time',
            'action',
            'is_pleasant',
            'related_habit',
            'periodicity',
            'reward',
            'time_to_complete',
            'is_public',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def validate(self, attrs):
        is_pleasant = attrs.get(
            'is_pleasant',
            getattr(self.instance, 'is_pleasant', False)
            if self.instance else False,
        )
        related = attrs.get(
            'related_habit',
            getattr(self.instance, 'related_habit', None)
            if self.instance else None,
        )
        reward = attrs.get(
            'reward',
            getattr(self.instance, 'reward', None)
            if self.instance else None,
        )

        validate_related_or_reward(is_pleasant, related, reward)
        return attrs


class HabitPublicSerializer(serializers.ModelSerializer):
    """Публичный список — только чтение."""

    class Meta:
        model = Habit
        fields = (
            'id',
            'place',
            'time',
            'action',
            'is_pleasant',
            'periodicity',
            'time_to_complete',
            'created_at',
        )
        read_only_fields = fields
