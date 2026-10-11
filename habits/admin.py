from django.contrib import admin
from .models import Habit, HabitLog


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'action', 'user', 'time', 'place',
        'is_pleasant', 'periodicity', 'is_public',
    )
    list_filter = ('is_pleasant', 'is_public', 'periodicity')
    search_fields = ('action', 'place', 'user__email')



@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'habit', 'date', 'completed', 'created_at')
    list_filter = ('completed', 'date')
