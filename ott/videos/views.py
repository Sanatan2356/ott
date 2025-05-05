from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import VideoSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from accounts.models import CustomUser
from .models import Video
import jwt
from django.conf import settings

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
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def list(self, request, *args, **kwargs):
        base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
        video_url = f"{base_url}/api/video/videos/"
        return Response({"videos": video_url})
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        video = self.get_object()
        video.views += 1
        video.save()
        return Response({
            "status_code": 200,
            "message": "Video views incremented",
            "views": video.views
        }, status=status.HTTP_200_OK)
