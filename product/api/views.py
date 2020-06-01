from django.shortcuts import redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics

from expert.models import Product
from .serializers import ProductSerializer

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@method_decorator(csrf_exempt, name='dispatch')
class ProductAssignAPIView(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Product
    http_method_names = ['get', 'post']
    permission_required = ('kit.view_kit','expert.view_product','expert.assign_product',)

    def get(self, *args, **kwargs):
        product = self.get_object()
        if self.kwargs['worker_pk'] == 0:
            product.unassign()
        return redirect(product.kit.get_absolute_url())

    def post(self, *args, **kwargs):
        product = self.get_object()
        if product.assignedto:
            # The product that user clicked has already been assigned to someone else.
            # check if worker has the permission to reassign product using change_product perm
            if self.request.user.has_perm('expert.change_product'):
                # Yes, the worker has the permission to reassign the products.
                # if the worker_pk is 0 then we have to change the product to pending
                if self.kwargs['worker_pk'] == 0:
                    product.unassign()
                    return redirect(product.kit.get_absolute_url())
                worker = Worker.objects.get(id=self.kwargs['worker_pk'])
                product.assign(worker)
                return JsonResponse({'assignedto': worker.username, 'refresh': False})
            else:
                # No, worker does'nt have the permission to change the assignment.
                # give a warning that product has already been assigned and refresh the page.
                return JsonResponse({'assignedto': None, 'refresh': True})
        worker = Worker.objects.get(id=self.kwargs['worker_pk'])
        product.assign(worker)
        # TODO: serialize the Worker model so I can directly pass it here.
        return JsonResponse({'assignedto': worker.username, 'refresh': False})