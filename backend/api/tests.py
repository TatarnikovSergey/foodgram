# backend/api/tests.py
from http import HTTPStatus
from django.test import Client, TestCase

from recipes import models


class FoodgramiAPITestCase(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.guest_client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_creation(self):
        """Проверка создания рецепта."""
        data = {'title': 'Test',
                'description': 'Test'}
        response = self.guest_client.post('/api/recipes/', data=data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(models.Recipies.objects.filter(name='Test').exists())
