from django.shortcuts import render
from rest_framework import generics, permissions, status
from .models import Artist, Artwork
from .serializers import ArtistSerializer, ArtworkSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

# -------------------------------
# Artist Registration
# -------------------------------
class RegisterArtistView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            artist = serializer.save()  # calls serializer.create()
            return Response({
                "message": "Registration successful",
                "id": artist.id,
                "username": artist.username,
                "email": artist.email,
                "bio": artist.bio,
                "profile_picture": artist.profile_picture.url if artist.profile_picture else None,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET → Retrieve own profile
    PUT/PATCH → Update username, email, bio, profile picture, password
    """
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.AllowAny]  # change to IsAuthenticated later

    lookup_field = 'id'  # You can use username instead if you prefe

# -------------------------------
# Artwork List / Create
# -------------------------------
class ArtworkListCreateView(generics.ListCreateAPIView):
    queryset = Artwork.objects.all().order_by('-created_at')
    serializer_class = ArtworkSerializer
    permission_classes = [permissions.AllowAny]  # change later if you want auth

    def perform_create(self, serializer):
        # Automatically assign an artist (temporary logic)
        artist = Artist.objects.first()  # later replace with: self.request.user
        serializer.save(artist=artist)

# -------------------------------
# Login
# -------------------------------
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                "message": "Login successful",
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import generics, permissions
from .models import Artist
from .serializers import ArtistSerializer

class ArtistDetailView(generics.RetrieveAPIView):
    """
    GET /api/artists/<username>/
    Returns artist profile info along with their artworks.
    """
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    lookup_field = 'username'
    permission_classes = [permissions.AllowAny]