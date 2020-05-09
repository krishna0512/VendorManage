from .models import Invoice

def model(request):
    return {'Invoice': Invoice}