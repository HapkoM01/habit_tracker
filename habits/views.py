from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Habit
from .serializers import HabitSerializer, HabitPublicSerializer
from .paginators import HabitPagination
from .permissions import IsOwnerOrReadOnlyPublic


@extend_schema_view(
    list=extend_schema(description='Список привычек текущего пользователя (пагинация по 5).'),
    create=extend_schema(description='Создание привычки.'),
    retrieve=extend_schema(description='Детали своей привычки.'),
    update=extend_schema(description='Полное обновление привычки.'),
    partial_update=extend_schema(description='Частичное обновление привычки.'),
    destroy=extend_schema(description='Удаление привычки.'),
)
class HabitViewSet(viewsets.ModelViewSet):
    """CRUD привычек текущего пользователя."""
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyPublic]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).select_related(
            'related_habit', 'user'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitListAPIView(generics.ListAPIView):
    """Список публичных привычек (только чтение)."""
    queryset = Habit.objects.filter(is_public=True).select_related('user')
    serializer_class = HabitPublicSerializer
    permission_classes = [AllowAny]
    pagination_class = HabitPagination
