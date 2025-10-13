from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Artist, Artwork
from io import BytesIO
from PIL import Image


class ArtworkCreationTestCase(APITestCase):
    """Test case for artwork creation to verify the artist argument bug is fixed"""
    
    def setUp(self):
        """Set up test client and create a test artist"""
        self.client = APIClient()
        # Create a test artist
        self.artist = Artist.objects.create_user(
            username='testartist',
            email='test@example.com',
            password='testpass123'
        )
        
    def create_test_image(self):
        """Helper method to create a test image file"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        return SimpleUploadedFile(
            name='test_image.png',
            content=image_file.read(),
            content_type='image/png'
        )
    
    def test_artwork_creation_authenticated(self):
        """Test that authenticated users can create artwork without duplicate artist error"""
        # Authenticate the client
        self.client.force_authenticate(user=self.artist)
        
        # Create test data
        image = self.create_test_image()
        data = {
            'title': 'Test Artwork',
            'image': image,
        }
        
        # Make POST request to create artwork
        response = self.client.post('/api/artworks/', data, format='multipart')
        
        # Print error details if test fails
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        
        # Assert the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Artwork')
        self.assertEqual(response.data['artist'], self.artist.id)
        
        # Verify artwork was created in database
        self.assertEqual(Artwork.objects.count(), 1)
        artwork = Artwork.objects.first()
        self.assertEqual(artwork.artist, self.artist)
        self.assertEqual(artwork.title, 'Test Artwork')
    
    def test_artwork_creation_unauthenticated(self):
        """Test that unauthenticated users cannot create artwork"""
        image = self.create_test_image()
        data = {
            'title': 'Test Artwork',
            'image': image,
        }
        
        # Make POST request without authentication
        response = self.client.post('/api/artworks/', data, format='multipart')
        
        # Assert the response is forbidden or unauthorized
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        # Verify no artwork was created
        self.assertEqual(Artwork.objects.count(), 0)
