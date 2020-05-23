from django.contrib import admin
from django.urls import reverse_lazy

from expert.models import *
from worker.models import Worker

# Register your models here.

admin.site.site_header = 'Expert Traders'
admin.site.index_title = 'Expert Traders Models'
admin.site.site_title = 'Expert Traders'

admin.site.register(Product)
admin.site.register(Worker)

admin.site.site_url = reverse_lazy('expert:index')
