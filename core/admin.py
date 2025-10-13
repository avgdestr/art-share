from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Artwork

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'profile_pic_preview', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)

    def profile_pic_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "No Image"
    profile_pic_preview.short_description = 'Profile Picture'


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'artist', 'created_at')
    search_fields = ('title', 'artist__username')
    list_filter = ('created_at',)
    
