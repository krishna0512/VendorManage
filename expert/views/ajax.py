from datetime import datetime, date
from django.http import JsonResponse
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from expert.models import Kit, Product
from worker.models import Worker
from invoice.models import Invoice
from expert.forms import *

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
class ProductCompleteView(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Product
    permission_required = ('expert.view_kit','expert.view_product','expert.complete_product',)

    def post(self, *args, **kwargs):
        if self.get_object().complete():
            product = self.get_object()
            return JsonResponse({
                'date_completed': product.date_completed.strftime("%b %d, %Y"),
                'completedby': product.completedby.username,
            })
        else:
            return JsonResponse({}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ProductAssignView(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Product
    http_method_names = ['post']
    pk_url_kwarg = 'product_pk'
    permission_required = ('expert.view_kit','expert.view_product','expert.assign_product',)

    def post(self, *args, **kwargs):
        product = self.get_object()
        if product.assignedto:
            # The product that user clicked has already been assigned to someone else.
            # check if worker has the permission to reassign product using change_product perm
            if self.request.user.has_perm('expert.change_product'):
                # Yes, the worker has the permission to reassign the products.
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

@method_decorator(csrf_exempt, name='dispatch')
class KitChangeCompletionDate(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Kit
    http_method_names = ['post']
    permission_required = ('expert.view_kit','expert.view_product','expert.change_kit',)

    def post(self, *args, **kwargs):
        kit = self.get_object()
        date = self.request.POST.get('date',None)
        date = datetime.strptime(date, '%Y-%m-%d').date()
        kit.date_product_completion = date
        kit.save()
        return JsonResponse({'date': date.strftime('%B %d, %Y')})