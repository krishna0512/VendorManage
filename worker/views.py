from datetime import date
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from expert.models import Kit
from .models import Worker
from expert.forms import *

class WorkerListView(PermissionRequiredMixin, ListView):
    queryset = Worker.objects.filter(active=True).order_by('first_name')
    navigation = ''
    permission_required = ('worker.view_worker')

class WorkerCreateView(PermissionRequiredMixin, CreateView):
    model = Worker
    fields = [
        'first_name','last_name','_username','address',
        'date_joined','photo',
    ]
    template_name_suffix = '_create_form'
    permission_required = ('worker.view_worker','worker.add_worker')

    def form_valid(self, form):
        form.instance._username = form.instance._username.lower()
        return super().form_valid(form)

class WorkerDetailView(PermissionRequiredMixin, DetailView):
    model = Worker
    permission_required = ('worker.view_worker')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ret = []
        worker = self.object
        kit_number_list = list(set([i.kit.number for i in worker.products_completed.all()]))
        kit_list = Kit.objects.filter(number__in=kit_number_list).order_by('-date_received')
        # kit_list = [Kit.objects.get(number=i) for i in kit_number_list]
        for i in kit_list:
            ret.append(
                {
                    'object': i,
                    'total_kit_contribution': sum([j.size for j in i.products.filter(completedby=worker)]),
                    'products_attached': i.products.filter(completedby=worker)
                }
            )
        context['data'] = ret
        context['products_completed'] = worker.products_completed.order_by('-kit__number', '-date_completed')
        context['kit_list'] = Kit.objects.filter(products__in=context['products_completed']).distinct().order_by('-number')
        return context

class WorkerUpdateView(PermissionRequiredMixin, UpdateView):
    model = Worker
    fields = [
        'first_name','last_name','_username','address',
        'date_joined','photo'
    ]
    template_name_suffix = '_update_form'
    permission_required = ('worker.view_worker','worker.change_worker')

    def form_valid(self, form):
        form.instance._username = form.instance._username.lower()
        return super().form_valid(form)

class WorkerDeleteView(PermissionRequiredMixin, DeleteView):
    model = Worker
    success_url = reverse_lazy('worker:list')
    permission_required = ('worker.view_worker','worker.delete_worker')

    def delete(self, request, *args, **kwargs):
        """
        Overwriting the delete method because once a worker is created
        it should not be deleted.
        only it should be rendered inactive.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.active = False
        self.object.save()
        return redirect(success_url)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)