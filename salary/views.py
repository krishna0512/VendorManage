from datetime import date
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

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