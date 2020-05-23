from expert.models import Product

def model(request):
    return {
        'Product': Product,
    }