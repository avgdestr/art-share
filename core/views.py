from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Artist, Artwork
from .serializers import ArtistSerializer, ArtworkSerializer, JWTLoginSerializer, PublicArtistSerializer



class RegisterArtistView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            try:
                artist = serializer.save()
                return Response({
                    "message": "Registration successful",
                    "id": artist.id,
                    "username": artist.username,
                    "email": artist.email,
                    "bio": artist.bio,
                    "profile_picture": artist.profile_picture.url if artist.profile_picture else None,
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Internal error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArtistDetailView(generics.RetrieveUpdateAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    lookup_field = 'username'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_object(self):
        try:
            obj = super().get_object()
        except Exception:
            raise NotFound("Artist not found.")
        if self.request.method in ['PUT', 'PATCH'] and obj != self.request.user:
            raise PermissionDenied("You can only update your own profile.")
        return obj

class ArtworkListCreateView(generics.ListCreateAPIView):
    queryset = Artwork.objects.all().order_by('-created_at')
    serializer_class = ArtworkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required to upload artwork.")
        try:
            serializer.save(artist=self.request.user)
        except Exception as e:
            raise serializers.ValidationError(f"Could not save artwork: {str(e)}")

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = JWTLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            access = serializer.validated_data["access"]
            refresh = serializer.validated_data["refresh"]
            return Response({
                "access": access,
                "refresh": refresh,
                "artist": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "bio": user.bio,
                    "profile_picture": user.profile_picture.url if user.profile_picture else None,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublicArtistDetailView(generics.RetrieveAPIView):
    queryset = Artist.objects.all()
    serializer_class = PublicArtistSerializer
    lookup_field = 'username'
    permission_classes = [permissions.AllowAny]
    def get_object(self):
        try:
            return super().get_object()
        except Exception:
            raise NotFound("Artist not found.")