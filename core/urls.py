from django.urls import path
from .views import (
    RegisterArtistView,
    ArtworkListCreateView,
    LoginView,
    ArtistDetailView,
    PublicArtistDetailView
)

urlpatterns = [
    path('register/', RegisterArtistView.as_view(), name='register'),
    path('artworks/', ArtworkListCreateView.as_view(), name='artworks'),
    path('login/', LoginView.as_view(), name='login'),

    # Authenticated retrieve/update/delete (GET, PATCH, PUT, DELETE) for the user's own profile
    path('artists/<str:username>/', ArtistDetailView.as_view(), name='artist-detail'),

    # Public read-only view of any artist profile
    path('artists/<str:username>/public/', PublicArtistDetailView.as_view(), name='public-artist-detail'),
]
