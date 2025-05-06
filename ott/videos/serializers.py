from rest_framework import serializers
from .models import Video,Favorite

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [ 'title', 'description', 'video_file', 'video_size', 'views', 'created_at']
        read_only_fields = [ 'video_size', 'views', 'created_at']  # Make these fields read-only

    def create(self, validated_data):
        video = Video.objects.create(**validated_data)
        return video


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = [ 'user', 'video', 'favorited_at']
        read_only_fields = ['favorited_at']
