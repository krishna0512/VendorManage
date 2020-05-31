from rest_framework import serializers, pagination
from ..models import Kit
from expert.models import Product
# from product.api.serializers import ProductSerializer

class KitSerializer(serializers.ModelSerializer):
    products = serializers.HyperlinkedRelatedField(many=True, view_name='expert:api-detail', read_only=True)
    # products = serializers.SerializerMethodField('paginated_products')

    class Meta:
        model = Kit
        fields = (
            'id', 'number', 'date_received', 'date_return',
            'products',
        )
    
#     def paginated_products(self, obj):
#         products = obj.products.all()
#         print(products)
#         paginator = pagination.PageNumberPagination()
#         page = paginator.paginate_queryset(products, self.context['request'])
#         print(page)
#         serializer = ProductSerializer(page, many=True, context={'request': self.context['request']})
#         print(serializer.data)
#         return serializer.data

# class ProductSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Product
#         fields = ('order_number',)