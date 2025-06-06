from rest_framework import serializers
from .models import Video,Favorite,Creator
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [ "creator","title", "description", "video_file", "video_size", "views", "created_at"]
        read_only_fields = ["video_size", "views", "created_at"]

    def create(self, validated_data):
        creator_instance = validated_data.get("creator")
        validated_data["creator_id"] = creator_instance.id
        video_file = validated_data.get("video_file")
        if video_file:
            validated_data["video_size"] = video_file.size
        return super().create(validated_data)

class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = [ 'name', 'role', 'about_us', 'views', 'total_videos']
        read_only_fields = ['total_videos']

    def create(self, validated_data):
        creator = Creator.objects.create(**validated_data)
        return creator



class VideoSimpleSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.name', read_only=True)

    class Meta:
        model = Video
        fields = ['title', 'creator_name']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = [ 'user', 'video', 'favorited_at']
        read_only_fields = ['favorited_at']


class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = ['name', 'role',  'total_videos', 'views']


class WatchVideoSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer()  # nested creator details

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'video_file', 'creator']

