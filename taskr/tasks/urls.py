from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^check/$',
        views.Checkpoint.as_view(),
        name='checkpoint'
    ),

    url(
        r'^tasks/$',
        views.TaskListCreate.as_view(),
        name='task-list'
    ),

    url(
        r'^tasks/(?P<pk>\d+)/$',
        views.TaskDetail.as_view(),
        name='task-detail'
    ),

    url(
        r'^tasks/(?P<pk>\d+)/assign/$',
        views.TaskAssign.as_view(),
        name='task-assign'
    ),

    url(
        r'^tasks/(?P<pk>\d+)/changestatus/$',
        views.TaskChangeStatus.as_view(),
        name='task-change-status'
    ),
]
