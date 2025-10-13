from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import Artist, Artwork
from .serializers import ArtistSerializer, ArtworkSerializer, LoginSerializer

# -------------------------------
# Artist Registration
# -------------------------------
class RegisterArtistView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            artist = serializer.save()
            return Response({
                "message": "Registration successful",
                "id": artist.id,
                "username": artist.username,
                "email": artist.email,
                "bio": artist.bio,
                "profile_picture": artist.profile_picture.url if artist.profile_picture else None,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Artist Detail / Update
# -------------------------------
class ArtistDetailView(generics.RetrieveUpdateAPIView):
    """
    GET → Retrieve artist profile
    PATCH/PUT → Update own profile
    """
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    lookup_field = 'username'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        """
        Ensure artists can only update their own profile
        """
        obj = super().get_object()
        if self.request.method in ['PUT', 'PATCH'] and obj != self.request.user:
            raise permissions.PermissionDenied("You can only update your own profile.")
        return obj


# -------------------------------
# Artwork List / Create
# -------------------------------
class ArtworkListCreateView(generics.ListCreateAPIView):
    queryset = Artwork.objects.all().order_by('-created_at')
    serializer_class = ArtworkSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        """
        Assign the authenticated user as the artist
        """
        if not self.request.user.is_authenticated:
            raise permissions.PermissionDenied("Authentication required to upload artwork.")
        serializer.save(artist=self.request.user)


# -------------------------------
# Login using JWT
# -------------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "artist": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
            }
        })


# -------------------------------
# Artist Public Info
# -------------------------------
class PublicArtistDetailView(generics.RetrieveAPIView):
    """
    GET /api/artists/<username>/
    Returns artist profile info (public)
    """
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    lookup_field = 'username'
    permission_classes = [permissions.AllowAny]
