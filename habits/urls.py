from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitListAPIView

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('habits/public/', PublicHabitListAPIView.as_view(), name='habit-public-list'),
    path('', include(router.urls)),
]
