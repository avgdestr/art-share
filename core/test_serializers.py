from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from core.serializers import ArtworkSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Artwork


User = get_user_model()


class ArtworkSerializerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', email='t@example.com', password='pass')

    def test_create_with_request_user(self):
        request = self.factory.post('/artworks/')
        request.user = self.user
        # minimal valid GIF image bytes (1x1 pixel)
        gif1x1 = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        )
        img = SimpleUploadedFile('test.gif', gif1x1, content_type='image/gif')
        data = {'title': 'Test Art', 'image': img}
        serializer = ArtworkSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        art = serializer.save()
        self.assertIsInstance(art, Artwork)
        self.assertEqual(art.artist, self.user)

    def test_create_with_explicit_artist_arg(self):
        # Ensure passing artist via save() doesn't cause a duplicate kwarg error
        request = self.factory.post('/artworks/')
        request.user = self.user
        gif1x1 = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        )
        img = SimpleUploadedFile('test2.gif', gif1x1, content_type='image/gif')
        data = {'title': 'Test Art 2', 'image': img}
        serializer = ArtworkSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        art = serializer.save(artist=self.user)
        self.assertIsInstance(art, Artwork)
        self.assertEqual(art.artist, self.user)
