from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Task
from tasks import enums


class UserReports(APIView):
    '''
    Reporting task info for authenticated user.

    Counts tasks for each user that are
      - created
      - assigned
      - completed
      - incompleted

    * Requires token authentication.
    '''
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        # Get queryset of tasks that user has created or assigned to.
        tasks = Task.objects.all()

        # Count the created tasks for a user.
        created_count = tasks.filter(reporter=user).count()

        # Count the assigned, completed, incompleted tasks for a user.
        # Derived from queryset of assigned tasks.
        assigned_tasks = tasks.filter(assignee=user)
        assigned_count = assigned_tasks.count()
        completed_count = assigned_tasks.filter(
            status=enums.STATUS_DONE
        ).count()
        incompleted_count = assigned_tasks.filter(
            status__in=[enums.STATUS_TODO, enums.STATUS_IN_PROGRESS]
        ).count()

        # Create response object.
        response = {}
        response['created'] = created_count
        response['assigned'] = assigned_count
        response['completed'] = completed_count
        response['incompleted'] = incompleted_count

        return Response(response, status=status.HTTP_200_OK)
