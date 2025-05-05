from django.urls import path,include
from .views import VideoUploadView,VideoViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='video')

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('', include(router.urls)),
]
