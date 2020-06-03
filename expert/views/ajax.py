from django.shortcuts import redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from datetime import datetime, date
import logging
logger = logging.getLogger(__name__)

from product.models import Product
from kit.models import Kit
from worker.models import Worker
from invoice.models import Invoice

def search(request):
    print('Hello')
    ret = []
    query = request.GET.get('query', None)
    if query is None:
        return JsonResponse({'suggestions': []})
    a = Product.objects.filter(order_number__icontains=query)
    for i in a:
        ret.append({
            'value': '{} ({})'.format(i.order_number.upper(), i.size),
            'data': {'category': '{} ({})'.format(i.kit.number, i.kit.date_received.strftime('%b %d, %Y'))},
            'url': i.get_absolute_url(),
        })
    return JsonResponse({'suggestions': ret})

def validate_create_worker_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': Worker.objects.filter(_username__iexact=username).exists()
    }
    return JsonResponse(data)

def email_invoice(request, pk):
    def get_emails(to):
        ret = to.strip().split(',')
        ret = [i.strip() for i in ret]
        return ret

    to = request.POST.get('to',None)
    o = get_email(to)
    subject = request.POST.get('subject','').strip()
    message = request.POST.get('message','').strip()
    Invoice.objects.get(id=pk).send_email(
        to=to,
        subject=subject,
        message=message,
        attach_invoice=True,
    )
    print(to, subject, message)
    return JsonResponse({'response': 'Email sent to {ret} Users'})

@method_decorator(csrf_exempt, name='dispatch')
class ProductUncompleteView(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Product
    permission_required = (
        'kit.view_kit', 'expert.view_product', 
        'expert.change_product',
    )

    def post(self, *args, **kwargs):
        if self.get_object().uncomplete():
            product = self.get_object()
            return JsonResponse({
                'id': product.id,
                'complete_url': product.get_complete_url(),
                'success': True,
            })
        else:
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ProductCompleteView(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Product
    permission_required = ('kit.view_kit','expert.view_product','expert.complete_product',)

    def post(self, *args, **kwargs):
        if self.get_object().complete():
            product = self.get_object()
            return JsonResponse({
                'uncomplete_url': product.get_uncomplete_url(),
                'date_completed': product.date_completed.strftime("%b %d, %Y"),
                'completedby': product.completedby.username,
            })
        else:
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ProductAssignView(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Product
    http_method_names = ['get', 'post']
    pk_url_kwarg = 'product_pk'
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