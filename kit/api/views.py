from rest_framework import generics

from ..models import Kit
from .serializers import KitSerializer

class KitListAPIView(generics.ListAPIView):
    queryset = Kit.objects.all()
    serializer_class = KitSerializer