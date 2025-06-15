from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()


class Creator(models.Model):
    name = models.CharField(max_length=100,unique=True)
    role = models.CharField(max_length=50)
    about_us = models.TextField(blank=True,max_length=100000)
    phone_number = models.CharField(max_length=15, blank=True, unique=True)
    total_videos = models.PositiveIntegerField(default=0)
    profile_image = models.ImageField(upload_to='creator_image/', blank=True, null=True)
    views = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Video(models.Model):
     # creator
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE) 

    title = models.CharField(max_length=255,unique=True)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    thumb_image = models.ImageField(upload_to='thumb_image/', blank=True, null=True)
    video_size = models.CharField(max_length=20, blank=True, null=True)  # e.g., "12 MB"
    views = models.PositiveIntegerField(default=0)  # count of views
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

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

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='favorited_by')
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')  

    def __str__(self):
        return f"{self.user.username} favorited {self.video.title}"


class Banner(models.Model):
    title=models.CharField(max_length=255,unique=True)
    banner_image=models.ImageField(upload_to='banner_images/', blank=True, null=True)

    def __str__(self):
        return self.title