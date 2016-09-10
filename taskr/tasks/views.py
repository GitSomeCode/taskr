from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.paginators import CustomPagination
from .enums import (
    EVENT_CREATED, EVENT_EDITED,
    EVENT_STATUS_CHANGED, EVENT_ASSIGNED
)
from .models import Task, TaskEventLog
from .serializers import (
    TaskSerializer,
    TaskStatusSerializer,
    TaskEventLogSerializer
)


User = get_user_model()


class Checkpoint(APIView):

    def get(self, request, format=None):
        response_data = {
            'message': "This is a test message"
        }
        return Response(response_data, status=status.HTTP_200_OK)


class TaskListCreate(generics.GenericAPIView):
    '''
    View to list all tasks if method is GET,
    or create a task if method is POST.

    * Requires token authentication.
    '''
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request, format=None):
        '''
        Returns paginated list of all tasks.
        '''
        tasks = Task.objects.all()

        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        '''
        Create a task.
        '''
        task_serializer = TaskSerializer(data=request.data)

        if task_serializer.is_valid():
            task = Task(**task_serializer.validated_data)
            task.reporter = request.user
            task.save()

            # Create TaskEventLog instance for create event.
            log = TaskEventLog(
                task=task,
                user=request.user,
                event=EVENT_CREATED,
                description='Task created.'
            )
            log.save()

            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            task_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TaskDetail(generics.GenericAPIView):
    '''
    Get, update or delete a task.

    * Requires token authentication.
    '''
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    lookup_field = 'pk'

    def get(self, request, pk):
        '''
        Get task detail.
        '''
        task = self.get_object()
        task_serializer = TaskSerializer(task)

        return Response(task_serializer.data)

    def put(self, request, pk):
        '''
        Update task.
        '''
        task = self.get_object()
        task_serializer = TaskSerializer(
            instance=task,
            data=request.data,
            partial=True
        )

        if task_serializer.is_valid():
            task_serializer.save()

            # Create TaskEventLog instance for update event.
            log = TaskEventLog(
                task=task,
                user=request.user,
                event=EVENT_EDITED,
                description='Task edited.'
            )
            log.save()

            return Response(task_serializer.data)

        return Response(
            task_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        '''
        Delete task.
        '''
        task = self.get_object()
        task.delete()

        return Response(
            {'id': '{}'.format(pk)},
            status=status.HTTP_200_OK
        )


class TaskAssign(generics.GenericAPIView):
    '''
    Assign a task to a User.

    * Requires token authentication.
    '''
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    lookup_field = 'pk'

    def post(self, request, pk):
        task = self.get_object()
        user = request.data.get('user')

        # Check if user is an empty string.
        try:
            user = get_object_or_404(User, pk=user)
        except ValueError:
            user = None

        # Check if user same as existing assignee.
        if task.assignee == user:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            task.assignee = user
            task.save()

            # Create TaskEventLog instance for assign event.
            log = TaskEventLog(
                task=task,
                user=request.user,
                event=EVENT_ASSIGNED,
                description='Task assigned to {}.'.format(user)
            )
            log.save()

            return Response(
                TaskSerializer(task).data
            )


class TaskChangeStatus(generics.GenericAPIView):
    '''
    Change the status of a Task.

    * Requires token authentication.
    '''
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    lookup_field = 'pk'

    def post(self, request, pk):
        task = self.get_object()
        task_serializer = TaskStatusSerializer(
            task,
            data=request.data,
            partial=True
        )

        if task_serializer.is_valid():

            # Check if new status same as existing status.
            if task_serializer.validated_data.get('status') == task.status:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                task = task_serializer.save()

                # Create TaskEventLog instance for status change event.
                log = TaskEventLog(
                    task=task,
                    user=request.user,
                    event=EVENT_STATUS_CHANGED,
                    description='Task status changed to "{}".'.format(
                        task_serializer.data
                    )
                )
                log.save()

                return Response(TaskSerializer(task).data)

        return Response(
            task_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TaskEventLogList(generics.GenericAPIView):
    '''
    Get event logs for a task.

    * Requires token authentication.
    '''
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    lookup_field = 'pk'

    def get(self, request, pk):
        task = self.get_object()

        logs = TaskEventLog.objects.select_related().filter(task=task)

        logs_serializer = TaskEventLogSerializer(logs, many=True)

        return Response(logs_serializer.data)


class UserReports(generics.GenericAPIView):
    '''
    Reporting task info for a user.

    * Requires token authentication.
    '''
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    lookup_field = 'username'

    def get(self, request, username):

        user = self.get_object()

        # Get queryset of tasks that user has created or assigned to.
        user_tasks = Task.objects.filter(
            Q(reporter=user) | Q(assignee=user)
        )

        # Count created, completed, and incompleted tasks of a user.
        created_tasks = user_tasks.filter(reporter=user).count()
        assigned_tasks = user_tasks.filter(assignee=user)
        completed_tasks = assigned_tasks.filter(status=3).count()
        incompleted_tasks = assigned_tasks.filter(status__in=[1, 2]).count()

        # Create response object.
        response = {}
        response['created'] = created_tasks
        response['completed'] = completed_tasks
        response['incompleted'] = incompleted_tasks

        return Response(response, status=status.HTTP_200_OK)
