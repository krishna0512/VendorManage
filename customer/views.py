from datetime import date
from django.shortcuts import redirect
from django.core.files import File
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import DeleteView, UpdateView, CreateView

from .models import Customer

class CustomerListView(ListView):
    model = Customer

class CustomerDetailView(DetailView):
    model = Customer

class CustomerCreateView(CreateView):
    model = Customer
    fields = '__all__'
    template_name_suffix = '_create_form'

class CustomerUpdateView(UpdateView):
    model = Customer
    fields = '__all__'
    template_name_suffix = '_update_form'