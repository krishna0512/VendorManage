from rest_framework import serializers
from django.urls import reverse
from expert.models import Product

class ProductSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField('get_absolute_url')
    complete_url = serializers.SerializerMethodField('get_complete_url')
    uncomplete_url = serializers.SerializerMethodField('get_uncomplete_url')
    return_url = serializers.SerializerMethodField('get_return_url')
    api_url = serializers.SerializerMethodField('get_api_url')

    def get_api_url(self, obj):
        return str(obj.get_api_url())

    def get_absolute_url(self, obj):
        return str(obj.get_absolute_url())
    def get_complete_url(self, obj):
        return str(obj.get_complete_url())
    def get_uncomplete_url(self, obj):
        return str(obj.get_uncomplete_url())
    def get_return_url(self, obj):
        return str(obj.get_return_url())


    class Meta:
        model = Product
        fields = (
            'id', 
            'name',
            'order_number',
            'quantity',
            'size',
            'fabric',
            'color',
            'status',
            'dispatched',
            'assignedto',
            'completedby',
            'date_completed',
            'date_shipped',
            'return_remark',
            'remark',
            'absolute_url',
            'complete_url',
            'uncomplete_url',
            'return_url',
            'api_url',
            'is_pending',
            'is_assigned',
            'is_completed',
            'is_returned',
            'is_dispatched',
        )