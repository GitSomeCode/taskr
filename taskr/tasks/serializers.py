from rest_framework import serializers

from .models import Task


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
