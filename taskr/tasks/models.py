from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from .enums import (
    PRIORITY_CHOICES, PRIORITY_MEDIUM,
    STATUS_CHOICES, STATUS_TODO,
    EVENT_CHOICES, EVENT_CREATED,
)


class Task(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)

    modified_on = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=300,
        verbose_name='Name',
        help_text='Task name'
    )

    description = models.TextField(
        max_length=2000,
        verbose_name='Description',
        help_text='Task description',
        blank=True
    )

    category = models.ForeignKey(
        'TaskCategory',
        related_name='tasks',
        on_delete=models.PROTECT,
        verbose_name='category',
        help_text='Task category'
    )

    priority = models.PositiveIntegerField(
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name='Priority',
        help_text='Task priority'
    )

    status = models.PositiveIntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_TODO,
        verbose_name='Status',
        help_text='Task status'
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_tasks',
        on_delete=models.PROTECT,
        verbose_name='Reporter',
        help_text='User that created the task'
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tasks',
        on_delete=models.PROTECT,
        verbose_name='Assignee',
        help_text='User that is assigned to the task',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return '{}'.format(self.name[:20])


class TaskCategory(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=100)

    description = models.TextField(
        max_length=300,
        blank=True
    )

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return '{}'.format(self.name[:20])


class TaskEventLog(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)

    task = models.ForeignKey(
        'Task',
        related_name='events',
        on_delete=models.CASCADE,
        verbose_name='Task',
        help_text='The task for this event'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='task_events',
        on_delete=models.CASCADE,
        verbose_name='User',
        help_text='The user that triggered the event'
    )

    event = models.PositiveIntegerField(
        choices=EVENT_CHOICES,
        default=EVENT_CREATED,
        verbose_name='Event',
        help_text='The event logged for this task'
    )

    description = models.TextField(
        max_length=2000,
        verbose_name='Description',
        help_text='Event description',
        blank=True
    )

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return '{}-{}'.format(self.task.name[:20], self.get_event_display())
