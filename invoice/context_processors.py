# from .models import Invoice
from expert.models import Invoice

def model(request):
    return {'Invoice': Invoice}