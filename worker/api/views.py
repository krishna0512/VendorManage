from rest_framework import generics

from ..models import Worker
from .serializers import WorkerSerializer

class WorkerListAPIView(generics.ListAPIView):
    queryset = Worker.objects.active()
    serializer_class = WorkerSerializer
    pagination_class = None

class WorkerDetailAPIView(generics.RetrieveAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer