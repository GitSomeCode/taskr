from django.conf.urls import url

from rest_framework.authtoken import views as rest_views

from . import views


urlpatterns = [
    url(
        r'^api-token-auth/',
        rest_views.obtain_auth_token
    ),

    url(
        r'^reports/$',
        views.UserReports.as_view(),
        name='user-reports'
    ),
]
