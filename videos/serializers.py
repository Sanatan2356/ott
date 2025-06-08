from rest_framework import serializers
from .models import Video,Favorite,Creator,Banner

class BannerAddSerializer(serializers.ModelSerializer):
    class Meta:
        model=Banner
        fields = ['title','banner_image']
        read_only_fields=['id']
    
    def create(self, validated_data):
            creator = Creator.objects.create(**validated_data)
            return creator

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title','banner_image']
  

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [ "id","title", "thumb_image" ,"views"]

class VideoAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [ "creator","title", "description", "video_file", "video_size", "views",'thumb_image' ,"created_at"]
        read_only_fields = ["video_size", "views", "created_at"]

    def create(self, validated_data):
        creator_instance = validated_data.get("creator")
        validated_data["creator_id"] = creator_instance.id
        video_file = validated_data.get("video_file")
        if video_file:
            validated_data["video_size"] = video_file.size
        return super().create(validated_data)


class CreatorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = ['id', 'name', 'role', 'about_us', 'views', 'total_videos']
        read_only_fields = ['total_videos']


class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = ['id', 'name', 'role', 'total_videos','profile_image']
        
  
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


class CreatorAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = ['name', 'role',  'total_videos','about_us', 'views','profile_image']

        def create(self, validated_data):
            creator = Creator.objects.create(**validated_data)
            return creator
        

class WatchVideoSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer()  # nested creator details

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'video_file', 'creator']

