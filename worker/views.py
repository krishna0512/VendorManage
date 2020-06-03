from datetime import date
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Worker
from expert.forms import *

import logging
logger = logging.getLogger(__name__)

class WorkerListView(PermissionRequiredMixin, ListView):
    queryset = Worker.objects.filter(active=True).order_by('first_name')
    navigation = 'worker'
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

    def has_permission(self):
        """Give the permission for a user to access his/her own page"""
        ret = super().has_permission()
        return ret or self.request.user.worker.pk == self.kwargs['pk']

    def get_context_data(self, **kwargs):
        kwargs['product_list'] = self.object.products_completed.order_by(
            '-kit__number', '-date_completed'
        )
        return super().get_context_data(**kwargs)

class WorkerReportView(PermissionRequiredMixin, View):
    permission_required = ('worker.view_worker')

    def has_permission(self):
        ret = super().has_permission()
        return ret or self.request.user.worker.pk == self.kwargs['pk']

    def get(self, *args, **kwargs):
        worker = Worker.objects.get(pk=self.kwargs['pk'])
        date_from = date.fromisoformat(self.request.GET.get('date_from', str(worker.date_joined)))
        date_to = date.fromisoformat(self.request.GET.get('date_to', str(date.today())))
        ptype = self.request.GET.get('type', 'all')
        print(date_from, date_to)
        data = []
        plist = worker.products_completed.get_date_completed_range(date_from, date_to)
        if ptype == 'dispatched':
            plist = plist.dispatched()
        elif ptype == 'remaining':
            plist = plist.remaining()
        elif ptype == 'completed':
            plist = plist.completed()
        elif ptype == 'returned':
            plist = plist.returned()
        for i in plist:
            data.append([
                i.kit.number,
                i.order_number,
                i.date_completed.strftime('%b %d, %Y'),
                i.quantity,
                i.size,
                i.get_return_remark_display() if i.is_returned else i.get_status_display(),
                i.remark
            ])
        return JsonResponse({'data': data})

class WorkerUpdateView(PermissionRequiredMixin, UpdateView):
    model = Worker
    fields = [
        'first_name','last_name','_username','address',
        'date_joined','photo', 'fixed_rate', 'variable_rate',
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
        logger.info('Deleting the Worker: {}'.format(self.object.username))
        success_url = self.get_success_url()
        self.object.active = False
        self.object.save()
        return redirect(success_url)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)