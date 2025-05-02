from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import VideoSerializer
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from accounts.models import CustomUser
from .models import Video
from .serializers import VideoSerializer
import jwt
from django.conf import settings

class VideoUploadView(APIView):
    # permission_classes = [IsAuthenticated]  # Ensure only authenticated users can upload videos

    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({"error": "Authorization header missing."}, status=status.HTTP_401_UNAUTHORIZED)

        if not auth_header.startswith('Bearer '):
            return Response({"error": "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            # Decode the refresh token manually
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Extract user info from the decoded token
            user_id = decoded_token.get('user_id')  
            print(user_id)
            user = CustomUser.objects.get(id=user_id)
            if not user.is_superuser:
                return Response({'message': 'Only admin can upload video.'}, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
        # Use the VideoSerializer to validate and create a new Video object
        request.user = user
        serializer = VideoSerializer(data=request.data)

        if serializer.is_valid():
            # Set the uploaded_by field to the currently authenticated user
            serializer.validated_data['uploaded_by'] = request.user
            video = serializer.save()  # Save the video to the database
            return Response({
                "message": "Video uploaded successfully.",
                "video": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users (admins) can access this

    def perform_create(self, serializer):
        # Set the uploaded_by field to the current user (admin)
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        video = self.get_object()
        video.views += 1
        video.save()
        return Response({"message": "Video views incremented", "views": video.views})