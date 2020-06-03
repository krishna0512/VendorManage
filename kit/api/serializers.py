from django.core.paginator import Paginator
from rest_framework import serializers, pagination
from ..models import Kit
from product.models import Product
# from product.api.serializers import ProductSerializer

class KitSerializer(serializers.ModelSerializer):
    # products = serializers.HyperlinkedRelatedField(many=True, view_name='expert:api-detail', read_only=True)
    products = serializers.SerializerMethodField('paginated_products')

    class Meta:
        model = Kit
        fields = (
            'id', 'number', 'date_received', 'date_return',
            'products',
        )
    
    def paginated_products(self, obj):
        products = obj.products.all()
        paginator = pagination.PageNumberPagination()
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100
        page = paginator.paginate_queryset(products, self.context['request'])
        page_size = int(self.context['request'].query_params.get('page_size') or 10)
        serializer = ProductSerializer(page, many=True, context={'request': self.context['request']})
        ret = paginator.get_paginated_response(serializer.data).data
        ret['num_pages'] = (obj.products.all().count() // page_size) + 1
        return ret

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    api_url = serializers.HyperlinkedIdentityField(view_name='expert:api-detail')

    class Meta:
        model = Product
        fields = ('id', 'api_url',)