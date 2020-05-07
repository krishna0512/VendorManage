from .models import Customer

def model(request):
    return {'Customer': Customer}