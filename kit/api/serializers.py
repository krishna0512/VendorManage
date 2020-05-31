from rest_framework import serializers
from ..models import Kit

class KitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kit
        fields = (
            'id', 'number', 'date_received', 'date_return',
        )