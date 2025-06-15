from django.urls import path,include
from .views import VideoUploadView,VideoViewSet,NewVideosView,ToggleFavoriteAPIView,WatchVideoAPIView,ViewFavoriteVideosAPIView,CreatorAddView,CreatorListView,CreatorDetailView,RecommendedVideosView,SearchVideosAPIView

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('favorite/', ToggleFavoriteAPIView.as_view(), name='toggle-favorite'),
    path('views/', VideoViewSet.as_view({'get': 'list'}),name="views-video"),
    path('favorites/', ViewFavoriteVideosAPIView.as_view(), name='view-favorites'),
    path('add-creator/', CreatorAddView.as_view(), name='add-creator'),
    path('creators/', CreatorListView.as_view(), name='creator-list'),
    path('creators/<str:name>/', CreatorDetailView.as_view(), name='creator-detail'),
    path('recommended/', RecommendedVideosView.as_view(), name='recommended-videos'),
    path('new-video/', NewVideosView.as_view(), name='view-all'),
    path('search_videos', SearchVideosAPIView.as_view(), name='search_videos'),
    path('watch/<int:video_id>/', WatchVideoAPIView.as_view(), name='watch-video'),

]


