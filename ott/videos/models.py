from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Video(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')  # creator
    title = models.CharField(max_length=255,unique=True)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    video_size = models.CharField(max_length=20, blank=True, null=True)  # e.g., "12 MB"
    views = models.PositiveIntegerField(default=0)  # count of views
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.video_file and not self.video_size:
            size_bytes = self.video_file.size
            if size_bytes < 1024:
                self.video_size = f"{round(size_bytes, 2)} B"
            elif size_bytes < 1024 * 1024:
                self.video_size = f"{round(size_bytes / 1024, 2)} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                self.video_size = f"{round(size_bytes / (1024 * 1024), 2)} MB"
            else:
                self.video_size = f"{round(size_bytes / (1024 * 1024 * 1024), 2)} GB"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
