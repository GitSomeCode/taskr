from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^check/$', views.Checkpoint.as_view(), name='checkpoint'),
    url(r'^tasks/$', views.TaskList.as_view(), name='task-list'),
    url(r'^task/(?P<pk>\d+)/$', views.task_detail, name='task-detail'),
]
