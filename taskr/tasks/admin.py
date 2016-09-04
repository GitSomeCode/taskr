from django.contrib import admin

from .models import Task, TaskCategory, TaskEventLog


class TaskAdmin(admin.ModelAdmin):
    pass


class TaskCategoryAdmin(admin.ModelAdmin):
    pass


class TaskEventLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskCategory, TaskCategoryAdmin)
admin.site.register(TaskEventLog, TaskEventLogAdmin)
