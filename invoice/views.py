from datetime import date
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView

from .models import Invoice
from challan.models import Challan
from .forms import InvoiceUpdateForm

class InvoiceCreateView(PermissionRequiredMixin, CreateView):
    model = Invoice
    fields = '__all__'
    template_name_suffix = '_create_form'
    permission_required = ('invoice.view_invoice','invoice.add_invoice')

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if Invoice.objects.all().exists():
            initial['number'] = Invoice.objects.all().order_by('-number').first().number + 1
        else:
            initial['number'] = 1
        initial['date_sent'] = date.today()
        initial['destination'] = 'Gandhinagar'
        initial['motor_vehicle_number'] = 'GJ-18-AU-3381'
        return initial

    def get_success_url(self):
        return self.object.get_absolute_url()

class InvoiceListView(PermissionRequiredMixin, ListView):
    model = Invoice
    navigation = 'invoice'
    ordering = ['-number']
    permission_required = ('invoice.view_invoice')

class InvoiceDetailView(PermissionRequiredMixin, DetailView):
    model = Invoice
    slug_field = 'number'
    navigation = 'invoice'
    permission_required = ('invoice.view_invoice','challan.view_challan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        challan_list = Challan.objects.filter(invoice=None)
        # this further filters the challan list to only the challans
        # that are compatible with challans already present in invoice.
        if self.object.challans.exists():
            challan_list = challan_list.filter(
                customer=self.object.challans.first().customer
            )
        context['challan_list'] = challan_list.order_by('-number')
        return context
    
class InvoiceChallanOperationView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Invoice
    pk_url_kwarg = 'invoice_pk'
    permission_required = (
        'invoice.view_invoice', 'challan.view_challan',
        'invoice.change_invoice', 'challan.change_challan',
    )

    def get_redirect_url(self, *args, **kwargs):
        invoice = self.get_object()
        challan = Challan.objects.get(id=self.kwargs['challan_pk'])
        if self.kwargs['operation'] == 'add':
            invoice.add_challan(challan)
        else:
            invoice.remove_challan(challan)
        return invoice.get_absolute_url()

class InvoicePrintableView(PermissionRequiredMixin, DetailView):
    model = Invoice
    slug_field = 'number'
    template_name_suffix = '_detail_printable'
    permission_required = ('invoice.view_invoice','challan.view_challan')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['challan_list'] = self.object.challans.order_by('number')
        return context

class InvoiceUpdateView(PermissionRequiredMixin, UpdateView):
    model = Invoice
    # fields = '__all__'
    form_class = InvoiceUpdateForm
    template_name_suffix = '_update_form'
    slug_field = 'number'
    permission_required = ('invoice.view_invoice','invoice.change_invoice')