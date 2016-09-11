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

    def test_create_tasks(self):
        url = reverse('task-list')
        data = {
            'name': 'Test Task 1',
            'description': 'Do this task first',
            'category': 1,
            'priority': 3,
            'status': 1,
            'reporter': self.user.pk,
            'assignee': None
        }

        # Check that task is created successfully by authorized user.
        response = self.client.post(url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(self.user.created_tasks.count(), 1)

        # Check that task cannot be created by unauthorized user.
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
