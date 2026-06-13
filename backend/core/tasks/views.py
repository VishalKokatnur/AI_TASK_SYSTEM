from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer
from users.permissions import IsAdmin
from analytics.models import ActivityLog

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'assigned_to']   # enables ?status=pending

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]        # only admin can create/delete
        return [IsAuthenticated()]    # any logged-in user can view/update

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Task.objects.all()                      # admin sees ALL
        return Task.objects.filter(assigned_to=user)       # user sees only theirs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)      # auto-set creator

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        # regular user can only update their OWN task
        if request.user.role != 'admin' and task.assigned_to != request.user:
            return Response({'error': 'Not allowed'}, status=403)
        ActivityLog.objects.create(
            user=request.user,
            action='task_update',
            detail=f"Task '{task.title}' → {request.data.get('status','')}"
        )
        return super().partial_update(request, *args, **kwargs)