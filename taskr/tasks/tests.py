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

        # Define headers
        self.headers = {
            'content-type': 'application/json',
            'secret-message': 'my-secret-message',
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.user.auth_token.key)
        }

    def test_get_tasks(self):
        url = reverse('task-list')

        # Check that status code for authorized request is OK.
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that status code for unauthorized request is UNAUTHORIZED.
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
