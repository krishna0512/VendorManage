from datetime import date
from django.urls import reverse_lazy
from django.views.generic import DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from expert.models import Product
from kit.models import Kit
from worker.models import Worker
from expert.forms import *

class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    model = Product
    fields = [
        'order_number','quantity','_size',
        'fabric','color', 'remark',
    ]
    template_name_suffix = '_update_form'
    permission_required = ('expert.view_product','expert.change_product')

    def form_valid(self, form):
        if form.instance.assignedto != form.instance.completedby:
            form.instance.assignedto = form.instance.completedby
        return super().form_valid(form)

class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    fields = [
        'order_number','quantity','_size',
        'fabric','color','status','assignedto',
        'completedby','date_completed','return_remark', 'remark',
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
    permission_required = ('kit.view_kit','expert.view_product','expert.delete_product')

    def delete(self, request, *args, **kwargs):
        # self.kit_number = self.get_object().kit.number
        self.success_url = self.get_object().kit.get_absolute_url()
        return super().delete(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class ProductDetailView(PermissionRequiredMixin, DetailView):
    model = Product
    permission_required = ('expert.view_product')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_superuser:
            worker_list = Worker.objects.active().order_by('first_name')
        else:
            worker_list = Worker.objects.filter(id=self.request.user.worker.id)
        context['worker_list'] = worker_list
        return context

class ProductReturnRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Product
    permission_required = ('kit.view_kit','expert.view_product','expert.change_product',)

    def get_redirect_url(self, *args, **kwargs):
        product = self.get_object()
        rr = self.request.GET.get('rr', '')
        product.return_product(rr)
        return product.kit.get_absolute_url()

class ProductSplitRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Product
    permission_required = (
        'kit.view_kit', 'expert.view_product',
        'expert.change_product'
    )

    def get_redirect_url(self, *args, **kwargs):
        product = self.get_object()
        factor = int(self.request.GET.get('factor',1))
        if factor==1 or product.quantity%factor or not product.is_pending or product.is_dispatched:
            return product.kit.get_absolute_url()
        # divide the product into factor parts.
        for i in range(factor):
            Product.objects.create(
                order_number=product.order_number,
                quantity=product.quantity//factor,
                _size=round(product.size/factor, 2),
                fabric=product.fabric,
                color=product.color,
                status=product.status,
                kit=product.kit,
            )
        ret = product.kit.get_absolute_url()
        product.delete()
        return ret