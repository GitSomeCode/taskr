import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tasks import enums
from tasks.models import Task, TaskCategory, TaskEventLog

User = get_user_model()


class UsersTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser',
            'testuser@email.com',
            'testuser',
            is_staff=True,
            is_superuser=True
        )

        self.url = reverse('user-reports')

        # Define headers.
        self.headers = {
            'content-type': 'application/json',
            'secret-message': 'my-secret-message',
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.user.auth_token.key)
        }

    def create_some_task(self, **kwargs):
        '''
        By default creates a task with
            name = "some task", description = "some description",
            category = "general", priority = "medium", status = "todo",
            reporter = self.user, assignee = None
        '''
        some_task = Task.objects.create(
            name=kwargs.get('name', 'some task'),
            description=kwargs.get('description', 'some description'),
            category=kwargs.get(
                'category',
                TaskCategory.objects.get(name='General')
            ),
            priority=kwargs.get('priority', enums.PRIORITY_MEDIUM),
            status=kwargs.get('status', enums.STATUS_TODO),
            reporter=kwargs.get('reporter', self.user),
            assignee=kwargs.get('assignee', None)
        )

        # Create TaskEventLog instance for create event.
        log = TaskEventLog(
            task=some_task,
            user=self.user,
            event=enums.EVENT_CREATED,
            description='Task created.'
        )
        log.save()

        return some_task

    def create_another_user(self, **kwargs):
        other_user = User.objects.create_user(
            username=kwargs.get('username', 'dummyuser'),
            email=kwargs.get('email', 'dummyemail@email.com'),
            password=kwargs.get('password', 'dummyuser'),
            is_staff=True,
            is_superuser=True
        )
        return other_user

    def create_dummy_user_report(self, **kwargs):
        dummy_response = {
            'assigned': kwargs.get('assigned', 0),
            'completed': kwargs.get('completed', 0),
            'incompleted': kwargs.get('incompleted', 0),
            'created': kwargs.get('created', 0)
        }
        return dummy_response

    def test_get_unauthorized_user_report(self):
        '''
        Test the GET method of UserReports view.
        Checks that unauthorized user cannot get user report.
        '''
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_empty_user_report(self):
        '''
        Test the GET method of UserReports view.
        Checks user report values.
        '''
        response = self.client.get(self.url, **self.headers)

        # empty user reports dictionary object.
        expected_response = self.create_dummy_user_report()

        # get updated task object from response.
        response_object = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_object, expected_response)

    def test_get_user_report(self):
        '''
        Test the GET method of UserReports view.
        Make some users, make some tasks, change statuses.
        Checks user report values.
        '''
        user1 = self.create_another_user(
            username='harry',
            email='harry@hogwarts.com',
            password='harrypassword'
        )
        user2 = self.create_another_user(
            username='draco',
            email='draco@hogwarts.com',
            password='dracopassword'
        )

        # t1 and t2 assigned to user, t3 created by user.
        t1 = self.create_some_task(reporter=user1)
        t2 = self.create_some_task(reporter=user2)
        t3 = self.create_some_task()

        # t1's status is not done i.e. incomplete.
        t1.assignee = self.user
        t1.status = enums.STATUS_IN_PROGRESS
        t1.save(update_fields=['assignee', 'status'])

        # t2's status is done i.e. complete.
        t2.assignee = self.user
        t2.status = enums.STATUS_DONE
        t2.save(update_fields=['assignee', 'status'])

        # user reports dictionary object.
        expected_response = self.create_dummy_user_report(
            assigned=2, created=1,
            completed=1, incompleted=1
        )

        response = self.client.get(self.url, **self.headers)

        # get updated task object from response.
        response_object = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_object, expected_response)
