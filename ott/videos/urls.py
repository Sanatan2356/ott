from django.urls import path,include
from .views import VideoUploadView,VideoViewSet,ToggleFavoriteAPIView,ViewFavoriteVideosAPIView


urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('favorite/', ToggleFavoriteAPIView.as_view(), name='toggle-favorite'),
    path('views/', VideoViewSet.as_view({'get': 'list'}),name="views-video"),
    path('favorites/', ViewFavoriteVideosAPIView.as_view(), name='view-favorites'),
]


