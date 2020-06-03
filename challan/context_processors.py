from .models import Challan

def model(request):
    return {'Challan': Challan}