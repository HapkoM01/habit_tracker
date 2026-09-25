from datetime import time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from habits.models import Habit

User = get_user_model()


class HabitAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@test.com', password='password123')
        self.other = User.objects.create_user(email='other@test.com', password='password123')
        self.pleasant = Habit.objects.create(
            user=self.user,
            place='дом',
            time=time(8, 0),
            action='выпить чай',
            is_pleasant=True,
            time_to_complete=60,
            periodicity=1,
        )
        self.habit = Habit.objects.create(
            user=self.user,
            place='парк',
            time=time(7, 0),
            action='пробежка',
            is_pleasant=False,
            reward='кофе',
            time_to_complete=90,
            periodicity=1,
            is_public=True,
        )

    def test_register(self):
        url = reverse('register')
        data = {
            'email': 'new@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_token(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': 'user@test.com',
            'password': 'password123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_list_own_habits(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('habit-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertLessEqual(len(response.data['results']), 5)

    def test_create_habit(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'офис',
            'time': '12:00:00',
            'action': 'разминка',
            'is_pleasant': False,
            'reward': 'яблоко',
            'time_to_complete': 60,
            'periodicity': 1,
        }
        response = self.client.post(reverse('habit-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user.id)

    def test_cannot_set_reward_and_related(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'дом',
            'time': '09:00:00',
            'action': 'чтение',
            'is_pleasant': False,
            'reward': 'чай',
            'related_habit': self.pleasant.id,
            'time_to_complete': 60,
            'periodicity': 1,
        }
        response = self.client.post(reverse('habit-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_time_to_complete_max_120(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'дом',
            'time': '09:00:00',
            'action': 'долгая',
            'time_to_complete': 200,
            'periodicity': 1,
        }
        response = self.client.post(reverse('habit-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_periodicity_max_7(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'дом',
            'time': '09:00:00',
            'action': 'редко',
            'time_to_complete': 60,
            'periodicity': 14,
        }
        response = self.client.post(reverse('habit-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pleasant_cannot_have_reward(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'дом',
            'time': '10:00:00',
            'action': 'музыка',
            'is_pleasant': True,
            'reward': 'ещё музыка',
            'time_to_complete': 30,
            'periodicity': 1,
        }
        response = self.client.post(reverse('habit-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_must_be_pleasant(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'зал',
            'time': '18:00:00',
            'action': 'тренировка',
            'is_pleasant': False,
            'related_habit': self.habit.id,  # не приятная
            'time_to_complete': 60,
            'periodicity': 1,
        }
        response = self.client.post(reverse('habit-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_own(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('habit-detail', args=[self.habit.id]),
            {'action': 'быстрая пробежка'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_own(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('habit-detail', args=[self.habit.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_access_foreign(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(reverse('habit-detail', args=[self.habit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_list(self):
        response = self.client.get(reverse('habit-public-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(any(h['action'] == 'пробежка' for h in results))

    def test_unauthenticated_list_denied(self):
        response = self.client.get(reverse('habit-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
