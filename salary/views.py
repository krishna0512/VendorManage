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

class SalaryListView(PermissionRequiredMixin, ListView):
    model = Salary
    ordering = ('-date_to')
    permission_required = (
        'salary.view_salary',
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            wpk = self.request.GET.get('worker_pk', None)
            if wpk:
                queryset = queryset.filter(worker__pk=wpk)
            return queryset
        else:
            return queryset.filter(worker__pk=self.request.user.worker.pk)

    def get_context_data(self, *args, **kwargs):
        wpk = self.request.GET.get('worker_pk', None)
        if wpk:
            kwargs['worker'] = Worker.objects.get(pk=wpk)
        return super().get_context_data(*args, **kwargs)

class SalaryCreateView(PermissionRequiredMixin, CreateView):
    model = Salary
    template_name_suffix = '_create_form'
    fields = [
        'worker', 'date_from', 'date_to',
        '_fixed_rate', '_variable_rate',
    ]
    permission_required = (
        'salary.add_salary', 'salary.view_salary',
    )
    success_url = reverse_lazy('salary:list')

    def get_context_data(self, *args, **kwargs):
        wpk = self.request.GET.get('worker_pk',None)
        if wpk:
            kwargs['worker'] = Worker.objects.get(pk=wpk)
        return super().get_context_data(*args, **kwargs)

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
            dt = date(dt.year, dt.month, 1) - timedelta(days=1)
            initial['date_from'] = df
            initial['date_to'] = dt
            initial['_fixed_rate'] = w.fixed_rate
            initial['_variable_rate'] = w.variable_rate
        return initial

class SalaryDetailView(PermissionRequiredMixin, DetailView):
    model = Salary
    permission_required = (
        'salary.view_salary',
    )

    def has_permission(self):
        ret = super().has_permission()
        if self.request.user.is_staff:
            # give the permission to vendor assuming its a staff
            return ret
        else:
            # else worker can only access his/her salary details
            return ret and self.request.user.worker == self.get_object().worker