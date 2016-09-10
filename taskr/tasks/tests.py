from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task

User = get_user_model()


class TasksTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser',
            'testuser@email.com',
            'testuser',
            is_staff=True,
            is_superuser=True
        )

    def test_get_tasks(self):
        url = reverse('task-list')
        token = self.user.auth_token

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
