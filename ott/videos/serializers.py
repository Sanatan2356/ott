from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [ 'title', 'description', 'video_file', 'video_size', 'views', 'created_at']
        read_only_fields = [ 'video_size', 'views', 'created_at']  # Make these fields read-only

    def create(self, validated_data):
        video = Video.objects.create(**validated_data)
        return video
