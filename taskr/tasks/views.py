from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskSerializer
from .models import Task


class Checkpoint(APIView):

    def get(self, request, format=None):
        response_data = {
            'message': "This is a test message"
        }
        return Response(response_data, status=status.HTTP_200_OK)


class TaskList(APIView):

    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


def task_detail(request, pk):
    pass
