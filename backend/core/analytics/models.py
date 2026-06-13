from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('upload', 'Document Upload'),
        ('search', 'Search'),
        ('task_update', 'Task Update'),
    ]
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action    = models.CharField(max_length=50, choices=ACTION_CHOICES)
    detail    = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"