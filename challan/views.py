from datetime import date
from django.shortcuts import redirect
from django.core.files import File
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import DeleteView, UpdateView

from kit.models import Kit
from .models import Challan
from customer.models import Customer
from . import process

class ChallanListView(PermissionRequiredMixin, ListView):
    model = Challan
    navigation = 'challan'
    ordering = ['-number']
    permission_required = ('challan.view_challan')

class ChallanDetailView(PermissionRequiredMixin, DetailView):
    model = Challan
    slug_field = 'number'
    permission_required = ('challan.view_challan','expert.view_product')


class ChallanUpdateView(PermissionRequiredMixin, UpdateView):
    model = Challan
    template_name_suffix = '_update_form'
    fields = [
        'number','date_sent','customer'
    ]
    permission_required = (
        'challan.view_challan', 'challan.change_challan',
    )

class ChallanPrintableView(PermissionRequiredMixin, DetailView):
    model = Challan
    slug_field = 'number'
    template_name_suffix = '_detail_printable'
    permission_required = ('challan.view_challan','expert.view_product')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ret = {}
        ret['max'] = {}
        ret['fab'] = {}
        ret['tuff'] = {}
        ret['clear'] = {}
        for fabric in ret:
            ret[fabric] = {
                'quantity': sum([i.quantity for i in self.object.products.filter(fabric=fabric, return_remark='')]),
                'size': round(sum([i.size for i in self.object.products.filter(fabric=fabric, return_remark='')]),2)
            }
        context['groupby_fabric'] = ret
        return context

class ChallanDeleteView(PermissionRequiredMixin, DeleteView):
    model = Challan
    slug_field = 'number'
    success_url = reverse_lazy('challan:list')
    permission_required = ('challan.view_challan','challan.delete_challan')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """TODO: I shouldnt have to reset the challan foreign key
        it should be done automatically but todo that we have to most probably change
        the on_delete attrib of challan in Product to somethingelse instead of CASCADE
        """
        self.object = self.get_object()
        for product in self.object.products.all():
            product.remove_challan()
        return super().delete(request, *args, **kwargs)

class ChallanCreateRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Kit
    permission_required = ('expert.view_kit','expert.view_product','challan.view_challan','challan.add_challan', 'expert.change_product')

    def _get_challan_number(self):
        if not Challan.objects.all().exists():
            return 51
        else:
            return Challan.objects.all().order_by('-number').first().number + 1

    def get_redirect_url(self, *args, **kwargs):
        kit = self.get_object()
        challan = Challan.objects.create(
            date_sent=date.today(),
            number=self._get_challan_number(),
        )
        for product in kit.products.all():
            product.add_challan(challan)
        challan.date_sent = max([i.date_completed for i in challan.products.all() if i.date_completed])
        # Auto select the default customer and if this doesnt exists 
        # then select the most recently added customer.
        if Customer.objects.exists():
            customer = None
            if Customer.objects.filter(default=True).exists():
                customer = Customer.objects.filter(default=True).first()
            else:
                # selects the most recently added customer
                customer = Customer.objects.all().order_by('-id').first()
            challan.customer = customer
        challan.save()
        return challan.get_absolute_url()


def challan_gatepass(request, pk):
    challan = Challan.objects.get(id=pk)
    img = challan.products.all().first().kit.jobwork_gatepass.path
    data = {
        'date': challan.date_sent.strftime('%d/%m/%Y'),
        'max_size': str(challan.get_total_size_by_fabric()['max']),
        'tuff_size': str(challan.get_total_size_by_fabric()['tuff']),
        'max_qty': sum([i.quantity for i in challan.products.filter(fabric='max', return_remark='')]),
        'tuff_qty': sum([i.quantity for i in challan.products.filter(fabric='tuff', return_remark='')]),
    }
    _, img = process.main(img, data=data)
    # tmp_dir = TemporaryDirectory(prefix='images')
    # out_image_path = os.path.join(tmp_dir.name, 'gatepass_processed.jpg')
    # cv.imwrite(out_image_path, img)
    # f = open(out_image_path, 'rb')
    f = open(img, 'rb')
    kit = challan.products.all().first().kit
    kit.jobwork_gatepass_processed.save('gatepass_processed.jpg', File(f))
    kit.save()
    return redirect(kit.jobwork_gatepass_processed.url)