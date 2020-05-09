from worker.models import Worker

def model(request):
    return {'Worker': Worker}