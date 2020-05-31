from rest_framework import serializers
from expert.models import Product

class ProductSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField('get_absolute_url')
    complete_url = serializers.SerializerMethodField('get_complete_url')
    uncomplete_url = serializers.SerializerMethodField('get_uncomplete_url')

    def get_absolute_url(self, obj):
        return str(obj.get_absolute_url())
    def get_complete_url(self, obj):
        return str(obj.get_complete_url())
    def get_uncomplete_url(self, obj):
        return str(obj.get_uncomplete_url())


    class Meta:
        model = Product
        fields = (
            'id', 
            'name',
            'order_number',
            'quantity',
            '_size',
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
        )