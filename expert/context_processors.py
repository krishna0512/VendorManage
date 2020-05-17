from expert.models import Kit, Product

def model(request):
    return {
        'Kit': Kit,
        'Product': Product,
    }