from django.db import models
from django.contrib.auth.models import AbstractUser


class Artist(AbstractUser):
    
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Artwork(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artworks')
    title = models.CharField(max_length=200)
    
    # Let Cloudinary's configured UPLOAD_OPTIONS.folder control the final
    # destination. Use empty upload_to to avoid creating a nested 'artshare/artshare'.
    image = models.ImageField(upload_to='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


