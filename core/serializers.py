from rest_framework import serializers
from .models import Artist, Artwork
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class ArtistSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = Artist
        fields = ['id', 'username', 'email', 'password', 'bio', 'profile_picture', 'created_at']
        extra_kwargs = {
            'bio': {'required': False},
            'profile_picture': {'required': False},
        }

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')
        if not username or not email or not password:
            raise serializers.ValidationError("Username, email, and password are required.")
        try:
            artist = Artist.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            artist.bio = validated_data.get('bio', '')
            artist.profile_picture = validated_data.get('profile_picture', None)
            artist.save()
            return artist
        except Exception as e:
            raise serializers.ValidationError(f"Could not create artist: {str(e)}")

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        try:
            instance.save()
        except Exception as e:
            raise serializers.ValidationError(f"Could not update artist: {str(e)}")
        return instance

class ArtworkSerializer(serializers.ModelSerializer):
    artist_username = serializers.CharField(source='artist.username', read_only=True)

    class Meta:
        model = Artwork
        fields = ['id', 'artist', 'artist_username', 'title', 'image', 'created_at']
        read_only_fields = ['artist', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to upload artwork.")
        # Remove 'artist' from validated_data to avoid duplicate keyword argument error
        # The artist is passed via serializer.save(artist=...) in the view
        validated_data.pop('artist', None)
        artist = request.user
        try:
            artwork = Artwork.objects.create(artist=artist, **validated_data)
            return artwork
        except Exception as e:
            raise serializers.ValidationError(f"Could not create artwork: {str(e)}")

class JWTLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = ArtistSerializer(read_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        refresh = RefreshToken.for_user(user)
        data["access"] = str(refresh.access_token)
        data["refresh"] = str(refresh)
        data["user"] = user
        return data