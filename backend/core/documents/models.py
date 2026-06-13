from django.db import models
from django.conf import settings

class Document(models.Model):
    title       = models.CharField(max_length=255)
    file_path   = models.CharField(max_length=500)
    content     = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title