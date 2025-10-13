from django.urls import path
from .views import (
    RegisterArtistView,
    ArtworkListCreateView,
    LoginView,
    ArtistDetailView,
    ArtistUpdateView
)


urlpatterns = [
    path('register/', RegisterArtistView.as_view(), name='register'),
    path('artworks/', ArtworkListCreateView.as_view(), name='artworks'),
    path('login/', LoginView.as_view(), name='login'),
    path('artists/<str:username>/', ArtistDetailView.as_view(), name='artist-detail'),
    path('artist/<int:id>/update/', ArtistUpdateView.as_view(), name='artist-update'),

 
]
