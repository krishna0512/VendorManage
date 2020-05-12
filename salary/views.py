from datetime import date
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from datetime import date
from dateutil.relativedelta import relativedelta as timedelta

from .models import Salary
from worker.models import Worker

# Create your views here.

class SalaryListView(ListView):
    model = Salary
    ordering = ('-date_to')

    def get_queryset(self):
        queryset = super().get_queryset()
        wpk = self.request.GET.get('worker_pk', None)
        if wpk:
            queryset = queryset.filter(worker__pk=wpk)
        return queryset

    def get_context_data(self, *args, **kwargs):
        wpk = self.request.GET.get('worker_pk', None)
        if wpk:
            kwargs['worker'] = Worker.objects.get(pk=wpk)
        return super().get_context_data(*args, **kwargs)

class SalaryCreateView(CreateView):
    model = Salary
    template_name_suffix = '_create_form'
    fields = [
        'worker', 'date_from', 'date_to',
        '_fixed_rate', '_variable_rate',
    ]
    success_url = reverse_lazy('salary:list')

    def get_context_data(self, *args, **kwargs):
        wpk = self.request.GET.get('worker_pk',None)
        if wpk:
            kwargs['worker'] = Worker.objects.get(pk=wpk)
        return super().get_context_data(*args, **kwargs)

    def form_valid(self, form):
        form.instance.populate_amount()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        wpk = self.request.GET.get('worker_pk', None)
        if wpk:
            w = Worker.objects.get(pk=wpk)
            initial['worker'] = w
            df = None
            if w.salaries.exists():
                df = w.salaries.order_by('-date_to').first().date_to + timedelta(days=1)
            else:
                df = w.date_joined
            dt = df + timedelta(months=1)
            dt = date(dt.year, dt.month, 1)
            dt -= timedelta(days=1)
            initial['date_from'] = df
            initial['date_to'] = dt
            initial['_fixed_rate'] = w.fixed_rate
            initial['_variable_rate'] = w.variable_rate
        return initial

class SalaryDetailView(DetailView):
    model = Salary