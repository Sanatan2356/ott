from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import VideoSerializer,FavoriteSerializer,BannerSerializer,BannerAddSerializer,VideoAddSerializer,CreatorAddSerializer,CreatorDetailSerializer,CreatorSerializer,WatchVideoSerializer,VideoSimpleSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from accounts.models import CustomUser
from .models import Video,Favorite,Creator,Banner
import jwt
from django.conf import settings
from permissions import IsJWTAuthenticated


class CreatorAddView(APIView):
    def post(self, request):
        # 🔐 Step 1: Auth check
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                "status_code": 401,
                "error": "Authorization header missing."
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not auth_header.startswith('Bearer '):
            return Response({
                "status_code": 401,
                "error": "Invalid token format."
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = CustomUser.objects.get(id=user_id)

            if not user.is_superuser:
                return Response({
                    "status_code": 403,
                    "message": "Only admin can add a creator."
                }, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({
                "status_code": 401,
                "error": "Token has expired."
            }, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.InvalidTokenError:
            return Response({
                "status_code": 401,
                "error": "Invalid token."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ Step 2: Process creation
        serializer = CreatorAddSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status_code": 201,
                "message": "Creator added successfully.",
                "creator": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status_code": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class VideoUploadView(APIView):
    def post(self, request):
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                "status_code": 401,
                "error": "Authorization header missing."
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not auth_header.startswith('Bearer '):
            return Response({
                "status_code": 401,
                "error": "Invalid token format."
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = CustomUser.objects.get(id=user_id)
            creator = Creator.objects.filter(phone_number=user.phone_number).first()
            creator_id=creator.id
            
            if not user.is_superuser and not user.is_creator:
                return Response({
                    "status_code": 403,
                    "message": "Only admin or creator only can upload video."
                }, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({
                "status_code": 401,
                "error": "Token has expired."
            }, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.InvalidTokenError:
            return Response({
                "status_code": 401,
                "error": "Invalid token."
            }, status=status.HTTP_401_UNAUTHORIZED)

        request.user = user
        serializer = VideoAddSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=creator) 
            video = serializer.save()
            # Update the related creator's total_videos count by 1
              # assuming Video has ForeignKey to Creator
            video.save()
            
            video.creator.total_videos += 1
            video.creator.save()

            return Response({
    "status_code": 201,
    "message": "Video uploaded successfully.",
    "video": {
        "id": video.id,
        "creator_name": video.creator.name,
        "title": video.title,
        "description": video.description,
        "video_file": video.video_file.url if video.video_file else None,
        "video_size": video.video_size,
        "views": video.views,
         "thumb_image":request.build_absolute_uri(serializer.data['thumb_image']),
        "created_at": video.created_at
    }
}, status=status.HTTP_201_CREATED)
        return Response({
            "status_code": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer

    def list(self, request, *args, **kwargs):
        
       
        user_id = IsJWTAuthenticated.has_permission(self,request)

        if user_id:
            queryset = Video.objects.all()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'status_code': 404, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    # @action(detail=True, methods=['post'])
    # def increment_views(self, request, pk=None):
    #     video = self.get_object()
    #     video.views += 1
    #     video.save()
    #     return Response({
    #         "status_code": 200,
    #         "message": "Video views incremented",
    #         "views": video.views
    #     }, status=status.HTTP_200_OK)


class ToggleFavoriteAPIView(APIView):
    def post(self, request):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        
        video_id = request.data.get('video_id')
        action =request.data.get('action')
        if not user_id or not video_id:
            return Response({"error": "user_id and video_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Toggle logic
        favorite, created = Favorite.objects.get_or_create(user_id=user_id, video_id=video_id)

        if action =='remove':
            # Already exists -> remove
            favorite.delete()
            return Response({"message": "Removed from favorites"}, status=status.HTTP_200_OK)
        elif action=='add':
            # Newly created
            serializer = FavoriteSerializer(favorite)
            return Response({"message": "Added to favorites", "data": serializer.data}, status=status.HTTP_201_CREATED)
        

class ViewFavoriteVideosAPIView(APIView):
    def get(self, request):
        user_id = IsJWTAuthenticated.has_permission(self, request)

        if not user_id:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        # Query all favorite videos for the authenticated user
        favorites = Favorite.objects.filter(user_id=user_id)

        # If no favorites found
        if not favorites.exists():
            return Response({"message": "No favorite videos found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the favorite video data
        serializer = FavoriteSerializer(favorites, many=True)

        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class CreatorListView(APIView):
    
    def get(self, request):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if user_id:    
            creators = Creator.objects.all()
            serializer = CreatorSerializer(creators, many=True)
            return Response({
                "status_code": 200,
                "creators": serializer.data
            }, status=status.HTTP_200_OK)

class CreatorDetailView(APIView):
    def get(self, request, name):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if user_id:    
            try:
                creator = Creator.objects.get(name=name)
            except Creator.DoesNotExist:
                return Response({
                    "status_code": 404,
                    "error": "Creator not found."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = CreatorSerializer(creator)
            return Response({
                "status_code": 200,
                "creator": serializer.data
            }, status=status.HTTP_200_OK)


class RecommendedVideosView(APIView):
    def get(self, request):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if user_id:   
            random_videos = Video.objects.order_by('?')[:5]  # randomly selects 5 videos
            serializer = VideoSerializer(random_videos, many=True)
            return Response({
                "status_code": 200,
                "recommended_videos": serializer.data
            }, status=status.HTTP_200_OK)
# new-videos/?limit=10
class NewVideosView(APIView):
    def get(self, request):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if user_id:
                
            # Get limit from query params, default to 5
            limit = int(request.query_params.get('limit', 5))

            # Get latest videos up to the limit
            latest_videos = Video.objects.order_by('-created_at')[:limit]
            serializer = VideoSerializer(latest_videos, many=True)

            return Response({
                "status_code": 200,
                "video_count": len(serializer.data),
                "recommended_videos": serializer.data
            }, status=status.HTTP_200_OK)
        
from django.db.models import Q


class SearchVideosAPIView(APIView):
    def get(self, request):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if user_id:
                
            query = request.GET.get('q')  # Get ?q=keyword from the URL
            videos = Video.objects.select_related('creator').order_by('-created_at')

            if query:
                videos = videos.filter(Q(title__icontains=query))
                # Return all matched results when query is provided
                serializer = VideoSimpleSerializer(videos, many=True)
            else:
                # Return only latest 5 if no query is given
                latest_videos = videos[:5]
                serializer = VideoSimpleSerializer(latest_videos, many=True)

            return Response({
                "status_code": 200,
                "results": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status_code": 404,
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

class WatchVideoAPIView(APIView):
    def get(self, request, video_id):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if user_id:
            try:
                video = Video.objects.select_related('creator').get(id=video_id)
            except Video.DoesNotExist:
                return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

            video_data = WatchVideoSerializer(video).data

            return Response({
                "video_details": {
                    "id": video_data['id'],
                    "title": video_data['title'],
                    "description": video_data['description'],
                    "video_url": video_data['video_file'],
                    'thumb_image':video_data['thumb_image'],
                    'views':video_data['views']
        
                },
                "creator_details": video_data['creator']
            }, status=status.HTTP_200_OK)
        

class BannerAddAPIView(APIView):
    def post(self, request):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if not user_id.is_superuser:
            return Response({
                    "status_code": 403,
                    "message": "Only admin can upload banner."
                }, status=status.HTTP_403_FORBIDDEN)
        serializer = BannerAddSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status_code": 201,
                "message": "Banner added successfully.",
                "creator": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status_code": 400,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class BannerListView(APIView):
    def get(self,request):
        user_id =IsJWTAuthenticated.has_permission(self,request)
        if not user_id:
            return Response({
                    "status_code": 404,
                    "message": "User not found"
                }, status=status.HTTP_403_FORBIDDEN)
       
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response({
            "status_code": 200,
            "banners": serializer.data
        }, status=status.HTTP_200_OK)