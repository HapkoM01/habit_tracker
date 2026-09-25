from rest_framework import serializers
from .models import Habit
from .validators import validate_time_to_complete, validate_periodicity


class HabitSerializer(serializers.ModelSerializer):
    time_to_complete = serializers.IntegerField(validators=[validate_time_to_complete])
    periodicity = serializers.IntegerField(validators=[validate_periodicity], default=1)

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
            getattr(self.instance, 'is_pleasant', False) if self.instance else False,
        )
        related = attrs.get(
            'related_habit',
            getattr(self.instance, 'related_habit', None) if self.instance else None,
        )
        reward = attrs.get(
            'reward',
            getattr(self.instance, 'reward', None) if self.instance else None,
        )

        if related and reward:
            raise serializers.ValidationError(
                'Нельзя одновременно указать связанную привычку и вознаграждение.'
            )

        if is_pleasant and reward:
            raise serializers.ValidationError(
                {'reward': 'У приятной привычки не может быть вознаграждения.'}
            )
        if is_pleasant and related:
            raise serializers.ValidationError(
                {'related_habit': 'У приятной привычки не может быть связанной привычки.'}
            )

        if related is not None and not related.is_pleasant:
            raise serializers.ValidationError(
                {'related_habit': 'Связанной может быть только приятная привычка.'}
            )

        return attrs


class HabitPublicSerializer(serializers.ModelSerializer):
    """Публичный список — без возможности редактирования."""

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
