from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import VideoSerializer,FavoriteSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from accounts.models import CustomUser
from .models import Video,Favorite
import jwt
from django.conf import settings
from permissions import IsJWTAuthenticated


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

            if not user.is_superuser:
                return Response({
                    "status_code": 403,
                    "message": "Only admin can upload video."
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
        serializer = VideoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data['uploaded_by'] = request.user
            serializer.save()
            return Response({
                "status_code": 201,
                "message": "Video uploaded successfully.",
                "video": serializer.data
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
