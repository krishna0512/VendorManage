from .models import Salary

def model(request):
    return {'Salary': Salary}