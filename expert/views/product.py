from datetime import date
from django.urls import reverse_lazy
from django.views.generic import DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from expert.models import Kit, Product
from expert.forms import *

class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    model = Product
    fields = [
        'order_number','quantity','size',
        'fabric','color'
    ]
    template_name_suffix = '_update_form'
    permission_required = ('expert.view_product','expert.change_product')

    def form_valid(self, form):
        if form.instance.return_remark:
            form.instance.status = 'returned'
        return super().form_valid(form)

class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    fields = [
        'order_number','quantity','size',
        'fabric','color','status','assignedto',
        'completedby','date_completed','return_remark'
    ]
    template_name_suffix = '_create_form'
    permission_required = ('expert.view_product','expert.add_product')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['kit'] = Kit.objects.get(number=self.kwargs['kit_number'])
        return context

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        initial['kit'] = Kit.objects.filter(number=self.kwargs['kit_number']).first()
        initial['fabric'] = 'max'
        return initial

    def get_success_url(self):
        if 'save_add_another' in self.request.POST:
            return reverse_lazy('expert:product-create', kwargs={'kit_number': self.kwargs['kit_number']})
        else:
            return self.object.kit.get_absolute_url()

    def form_valid(self, form):
        form.instance.kit = Kit.objects.get(number=self.kwargs['kit_number'])
        # form.instance.kit = Kit.objects.filter(number=self.kwargs['kit_number']).first()
        return super().form_valid(form)

class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = Product
    permission_required = ('expert.view_kit','expert.view_product','expert.delete_product')

    def delete(self, request, *args, **kwargs):
        # self.kit_number = self.get_object().kit.number
        self.success_url = self.get_object().kit.get_absolute_url()
        return super().delete(request, *args, **kwargs)

    # def get_success_url(self):
    #     return Kit.objects.filter(number=self.kit_number).first().get_absolute_url()

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class ProductDetailView(PermissionRequiredMixin, DetailView):
    model = Product
    permission_required = ('expert.view_product')

class ProductReturnRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Product
    permission_required = ('expert.view_kit','expert.view_product','expert.change_product',)

    def get_redirect_url(self, *args, **kwargs):
        product = self.get_object()
        rr = self.request.GET.get('rr', '')
        product.return_product(rr)
        return product.kit.get_absolute_url()