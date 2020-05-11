from datetime import date
from django.shortcuts import redirect
from django.core.files import File
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import DeleteView, UpdateView, CreateView

from .models import Customer

class CustomerListView(PermissionRequiredMixin, ListView):
    model = Customer
    navigation = 'customer'
    permission_required = (
        'customer.view_customer',
    )

class CustomerDetailView(PermissionRequiredMixin, DetailView):
    model = Customer
    permission_required = (
        'customer.view_customer',
    )

class CustomerCreateView(PermissionRequiredMixin, CreateView):
    model = Customer
    fields = '__all__'
    template_name_suffix = '_create_form'
    permission_required = (
        'customer.view_customer', 'customer.add_customer',
    )

class CustomerUpdateView(PermissionRequiredMixin, UpdateView):
    model = Customer
    fields = '__all__'
    template_name_suffix = '_update_form'
    permission_required = (
        'customer.view_customer', 'customer.change_customer',
    )