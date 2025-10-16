from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response


class HealthCheckView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({
            "cloudinary_configured": bool(getattr(settings, 'CLOUDINARY_CONFIGURED', False)),
            "default_file_storage": getattr(settings, 'DEFAULT_FILE_STORAGE', None),
        })
