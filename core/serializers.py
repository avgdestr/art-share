from rest_framework import serializers
from .models import Artist, Artwork
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


class ArtistSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = Artist
        fields = ['id', 'username', 'email', 'password', 'bio', 'profile_picture', 'created_at']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'bio': {'required': False},
            'profile_picture': {'required': False},
        }

    def create(self, validated_data):
        artist = Artist.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        artist.bio = validated_data.get('bio', '')
        artist.profile_picture = validated_data.get('profile_picture', None)
        artist.save()
        return artist

    def update(self, instance, validated_data):
        """
        Allow artists to update their username, bio, email, password, or profile picture.
        """
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


# --- IGNORE ---
class ArtworkSerializer(serializers.ModelSerializer):
    artist_username = serializers.CharField(source='artist.username', read_only=True)

    class Meta:
        model = Artwork
        fields = ['id', 'artist', 'artist_username', 'title', 'image', 'created_at']
        read_only_fields = ['artist', 'created_at']

    def create(self, validated_data):
        """
        Create an Artwork and set the artist from request.user (serializer context).
        DRF generic views pass 'request' in serializer context automatically.
        """
        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to upload artwork.")
        artist = request.user
        # create the artwork with artist set by the server (not from client)
        artwork = Artwork.objects.create(artist=artist, **validated_data)
        return artwork
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        # Check that both fields are provided
        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        # Authenticate the user (checks username + password)
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        data["user"] = user
        return data

