from .models import Kit

def model(request):
    return {'Kit': Kit}