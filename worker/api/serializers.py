from django.core.paginator import Paginator
from rest_framework import serializers, pagination
from ..models import Worker

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'address',
            'date_joined',
            'date_left',
            'aadhar_number',
            'mobile_number',
            'active',
        )