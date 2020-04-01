from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.dates import MonthArchiveView, DayArchiveView

from expert.models import Kit, Product, Worker

# Create your views here.

class IndexTemplateView(TemplateView):
    template_name='expert/index.html'

class KitListView(ListView):
    model = Kit

class KitCreateView(CreateView):
    model = Kit
    fields = '__all__'
    template_name_suffix = '_create_form'

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        n = max([i.number for i in Kit.objects.all()])+1
        initial['number'] = str(n)
        return initial

class KitUpdateView(UpdateView):
    model = Kit
    fields = '__all__'
    template_name_suffix = '_update_form'

class KitDetailView(DetailView):
    model = Kit
    slug_field = 'number'

class ProductUpdateView(UpdateView):
    model = Product
    fields = '__all__'
    template_name_suffix = '_update_form'

class ProductCreateView(CreateView):
    model = Product
    fields = '__all__'
    template_name_suffix = '_create_form'

def product_complete(request, pk):
    p = Product.objects.get(id=pk)
    p.completedby = p.assignedto
    p.completeddate = datetime.now()
    p.save()
    return redirect(p.kit.get_absolute_url())

class ProductDayArchiveView(DayArchiveView):
    model = Product
    date_field = 'completeddate'
    template_name_suffix = '_report_day'

    def get_context_data(self, *args, **kwargs):
        worker_list = []
        context = super().get_context_data(*args, **kwargs)
        for worker in Worker.objects.all():
            p = Product.objects.filter(completedby=worker).filter(completeddate=context['day'])
            ret = {}
            ret['name'] = worker.get_fullname()
            if p.exists():
                ret['daily_work'] = sum([i.size for i in p])
            else:
                ret['daily_work'] = 0.0
            worker_list.append(ret)
        context['worker_list'] = worker_list
        return context

class WorkerDetailView(DetailView):
    model = Worker

class WorkerListView(ListView):
    model = Worker
