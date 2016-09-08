from rest_framework import serializers

from .models import Task, TaskEventLog


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id', 'name', 'description', 'category',
            'priority', 'status', 'reporter', 'assignee'
        )
        read_only_fields = ('id', 'status', 'reporter', 'assignee')


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('status',)


class TaskEventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskEventLog
        fields = ('task', 'user', 'event', 'description')
