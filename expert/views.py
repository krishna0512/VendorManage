from datetime import datetime, timedelta, date
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.core.files import File
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.dates import MonthArchiveView, DayArchiveView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from expert.models import Kit, Product, Worker, Challan, Invoice
from expert.forms import *
from expert import process
from random import random

# Create your views here.

def validate_create_worker_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': Worker.objects.filter(_username__iexact=username).exists()
    }
    return JsonResponse(data)

def  send_email(request):
    ret = send_mail(
        subject='test',
        message='Hi, This is a test message from Auto Django.',
        from_email='kt.krishna.tulsyan@gmail.com',
        recipient_list=['expertcovers2020@gmail.com'],
        fail_silently=False
    )
    return JsonResponse({'response': 'Email sent to {ret} Users'})

def email_invoice(request, pk):
    def get_emails(to):
        ret = to.strip().split(',')
        ret = [i.strip() for i in ret]
        return ret

    to = request.POST.get('to',None)
    to = get_email(to)
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

class IndexTemplateView(LoginRequiredMixin, TemplateView):
    template_name='expert/index.html'

class KitListView(PermissionRequiredMixin, ListView):
    model = Kit
    # for navigation active display
    navigation = 'kit'
    ordering = ['-number']
    permission_required = ('expert.view_kit')

class KitCreateView(PermissionRequiredMixin, CreateView):
    model = Kit
    fields = '__all__'
    template_name_suffix = '_create_form'
    permission_required = ('expert.view_kit','expert.add_kit')

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if Kit.objects.all().exists():
            n = max([i.number for i in Kit.objects.all()])+1
        else:
            n = 1
        initial['number'] = str(n)
        initial['date_received'] = date.today()
        return initial

    def process_excel_data(self, data):
        def _select_fabric(fab):
            """Internal Function to correctly select the fabric"""
            fab = fab.lower()
            if fab in ['max','cover max','covermax']:
                return 'max'
            elif fab in ['tuff','cover tuff','covertuff','tuf','cover tuf']:
                return 'tuff'
            elif fab in ['fab','cover fab','coverfab']:
                return 'fab'
            elif fab in ['clear','cover clear','coverclear']:
                return 'clear'
            else:
                # return default max if none matches
                return 'max'
        def _select_color(col):
            """Internal Function to correctly select the color from data"""
            col = col.lower()
            if ' ' in col:
                if 'gray' in col or 'grey' in col:
                    return 'light_gray'
                else:
                    return col.replace(' ','_')
            else:
                if col in ['beige','biege']:
                    return 'beige'
                elif col in ['gray','grey']:
                    return 'gray'
                elif col in ['burgundy','burgandy']:
                    return 'burgundy'
                elif col in ['coffee','cofee','coffe','cofe']:
                    return 'coffee_brown'
                elif col == 'olive':
                    return 'olive_green'
                else:
                    return col

        data = data.strip().split('\n')
        for row in data:
            r = row.strip().split('\t')
            r = [i.strip() for i in r]
            Product.objects.create(
                order_number=r[0].upper(),
                quantity=int(r[1]),
                size=float(r[2]),
                fabric=_select_fabric(r[3]),
                color=_select_color(r[4]),
                # fabric=r[3].split()[1].lower(),
                # color=r[4].lower(),
                kit=self.object,
            )

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.data:
            self.process_excel_data(self.object.data)
        return response

class KitUpdateView(PermissionRequiredMixin, UpdateView):
    model = Kit
    slug_field = 'number'
    fields = [
        'number','date_received','date_product_completion',
        'jobwork_gatepass'
    ]
    template_name_suffix = '_update_form'
    permission_required = ('expert.view_kit','expert.change_kit')

class KitDetailView(PermissionRequiredMixin, DetailView, MultipleObjectMixin):
    model = Kit
    slug_field = 'number'
    paginate_by = 10
    permission_required = ('expert.view_kit','expert.view_product')

    def apply_filters(self, queryset, filters):
        def filter_status(q, s):
            if s=='dispatched':
                return Q(dispatched=True)
            if s=='completed':
                return Q(dispatched=False)&Q(status=s)
            return Q(status=s)
            # return q.filter(status=s)
        def filter_fabric(q, f):
            return Q(fabric=f)
            # return q.filter(fabric=f)

        if not ':' in filters:
            return Q()
        if filters.split(':')[0].strip() == 'status':
            queryset = filter_status(queryset, filters.split(':')[1].strip())
        elif filters.split(':')[0].strip() == 'fabric':
            queryset = filter_fabric(queryset, filters.split(':')[1].strip())
        return queryset

    def get_context_data(self, *args, **kwargs):
        object_list = Product.objects.filter(kit=self.object).order_by('id')
        if self.request.GET.get('filters',None):
            filterq = self.apply_filters(object_list, self.request.GET.get('filters',None))
        else:
            filterq = Q()
        # context = super().get_context_data(object_list=object_list, **kwargs)
        context = {}
        if self.request.user.is_superuser:
            worker_list = Worker.objects.filter(active=True).order_by('first_name')
            object_list = object_list.filter(filterq)
            # context['product_list'] = context['object_list']
        else:
            worker_list = Worker.objects.filter(id__in=[self.request.user.worker.id])
            # a BaseWorker can only view the products that are pending, and the products that
            # are completedby or assignedto the particular worker.
            q = Q(status='pending') | Q(assignedto=self.request.user.worker) | Q(completedby=self.request.user.worker)
            object_list = object_list.filter(filterq & q)
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['worker_list'] = worker_list
        context['product_list'] = context['object_list']
        return context

class KitDeleteView(PermissionRequiredMixin, DeleteView):
    model = Kit
    slug_field = 'number'
    success_url = reverse_lazy('expert:kit-list')
    permission_required = ('expert.view_kit','expert.delete_kit')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

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

@method_decorator(csrf_exempt, name='dispatch')
class ProductCompleteView(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Product
    permission_required = ('expert.view_kit','expert.view_product','expert.complete_product',)

    def post(self, *args, **kwargs):
        self.get_object().complete()
        return JsonResponse({'saved': True})

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
                product.assign(worker.id)
                return JsonResponse({'assignedto': worker.username, 'refresh': False})
            else:
                # No, worker does'nt have the permission to change the assignment.
                # give a warning that product has already been assigned and refresh the page.
                return JsonResponse({'assignedto': None, 'refresh': True})
        worker = Worker.objects.get(id=self.kwargs['worker_pk'])
        product.assign(worker.id)
        # TODO: serialize the Worker model so I can directly pass it here.
        return JsonResponse({'assignedto': worker.username, 'refresh': False})

class ProductReturnRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Product
    permission_required = ('expert.view_kit','expert.view_product','expert.change_product',)

    def get_redirect_url(self, *args, **kwargs):
        product = self.get_object()
        rr = self.request.GET.get('rr', '')
        product.return_product(rr)
        return product.kit.get_absolute_url()

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

# TODO: add a function in product model for completeing and uncompleting the product
class KitUncompleteRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Kit
    permission_required = ('expert.view_kit','expert.view_product','expert.change_product',)

    def get_redirect_url(self, *args, **kwargs):
        kit = self.get_object()
        for product in kit.products.all():
            product.uncomplete()
        return kit.get_absolute_url()


class ChallanInitRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Kit
    permission_required = ('expert.view_kit','expert.view_product','expert.view_challan','expert.add_challan', 'expert.change_product')

    def _get_challan_number(self):
        if not Challan.objects.all().exists():
            return 51
        else:
            return Challan.objects.all().order_by('-number').first().number + 1

    def get_redirect_url(self, *args, **kwargs):
        kit = self.get_object()
        challan = Challan.objects.create(
            date_sent=datetime.now(),
            number=self._get_challan_number(),
        )
        for product in kit.products.all():
            product.add_challan(challan.id)
        challan.date_sent = max([i.date_completed for i in challan.products.all() if i.date_completed])
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

class ProductDayArchiveView(DayArchiveView):
    model = Product
    date_field = 'date_completed'
    # TODO: check if allow_empty should be allowed or not
    allow_empty = True
    allow_future = True
    template_name_suffix = '_report_day'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # worker_list = []
        # for worker in Worker.objects.all():
        #     p = Product.objects.filter(completedby=worker).filter(date_completed=context['day'])
        #     ret = {}
        #     ret['name'] = worker.get_fullname()
        #     if p.exists():
        #         ret['daily_work'] = sum([i.size for i in p])
        #     else:
        #         ret['daily_work'] = 0.0
        #     worker_list.append(ret)
        # context['worker_list'] = worker_list
        #TODO: Improve the worker_list to exclude the inactive worker somehow.
        context['worker_list'] = Worker.objects.all()
        return context

class ProductMonthArchiveView(MonthArchiveView):
    model = Product
    date_field = 'date_completed'
    allow_empty = True
    allow_future = True
    template_name_suffix = '_report_month'

    # TODO: convert these methods to Manager methods of Product
    def get_product_completed(self, start_date, end_date):
        # ret = Product.objects.get_date_completed_range(start_date, end_date)
        # ret = ret.filter(status__in=['completed','dispatched'])
        # return ret
        d = start_date
        ret = []
        while d <= end_date:
            x = Product.objects.filter(date_completed=d)
            if not x.exists():
                ret.append(0)
            else:
                x = round(sum([i.size for i in x]), 2)
                ret.append(x)
            d += timedelta(days=1)
        return ret
    
    def get_product_returned(self, start_date, end_date):
        # ret = Product.objects.get_date_completed_range(start_date, end_date).exclude(return_remark='')
        # return ret
        d = start_date
        ret = []
        while d <= end_date:
            x = Product.objects.filter(date_completed=d).exclude(return_remark='')
            if not x.exists():
                ret.append(0)
            else:
                x = round(sum([i.size for i in x]), 2)
                ret.append(x)
            d += timedelta(days=1)
        return ret

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        start_date = context['month']
        end_date = context['next_month'] - timedelta(days=1)
        # print(list(range(start_date, end_date, timedelta(days=1))))
        dl = []
        d = start_date
        while d <= end_date:
            dl.append(d)
            d += timedelta(days=1)
        dl = [str(i.day) for i in dl]
        for i in range(9):
            dl[i] = '0{}'.format(dl[i])
        chart_data = {}
        chart_data['date_list'] = str(dl)
        chart_data['product_completed'] = str(self.get_product_completed(start_date, end_date))
        chart_data['product_returned'] = str(self.get_product_returned(start_date, end_date))
        r = Product.objects.filter(date_completed__lte=end_date, date_completed__gte=start_date)
        context['kit_list'] = Kit.objects.get_date_received_range(start_date, end_date).order_by('date_received')
        kit_list = context['kit_list']
        context['kits_received'] = Kit.objects.filter(date_received__gte=start_date, date_received__lte=end_date).count()
        context['total_product_completed'] = sum([i.size_detail['completed'] for i in kit_list])
        context['total_product_returned'] = sum([i.size_detail['returned'] for i in kit_list])
        context['total_product_received'] = sum([i.size for i in kit_list])
        context['total_product_dispatched'] = sum([i.size_detail['dispatched'] for i in kit_list])
        # context['total_product_completed'] = sum([i.size for i in r.filter(return_remark='')])
        # context['total_product_returned'] = sum([i.size for i in r.exclude(return_remark='')])
        # context['total_product_accepted'] = sum([i.size for i in r])
        try:
            context['product_completed_percent'] = context['total_product_completed']*100 // context['total_product_received']
            context['product_returned_percent'] = context['total_product_returned']*100 // context['total_product_received']
        except ZeroDivisionError:
            context['product_completed_percent'] = 100
            context['product_returned_percent'] = 0
        worker_list = Worker.objects.active().order_by('_username')
        a = []
        for worker in worker_list:
            a.append({
                'worker': worker,
                'completed': worker.get_date_completed_product_range(start_date, end_date).completed().dispatched().size,
                'returned': worker.get_date_completed_product_range(start_date, end_date).returned().dispatched().size,
            })
        context['worker_list'] = a
        print(a)
        # d = start_date
        # pc = []
        # while d <= end_date:
        #     x = Product.objects.filter(date_completed=d)
        #     x = [i.size for i in x]
        #     x = sum(x)
        #     x = round(x, 2)
        #     pc.append(x)
        #     d += timedelta(days=1)
        # chart_data['product_completed'] = str(pc)
        # context['date_list_string'] = str(dl)
        # data = [int(random()*100) for i in range(30)]
        # context['data'] = str(data)
        context['chart_data'] = chart_data
        return context

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     context['worker_list'] = Worker.objects.all().order_by('first_name')
    #     start_date = context['month']
    #     end_date = context['next_month'] - timedelta(days=1)
    #     data = []
    #     dd = start_date
    #     d_list = []
    #     while dd <= end_date:
    #         d_list.append(dd)
    #         data.append(
    #             {
    #                 'date': dd,
    #                 'contributions': [sum([i.size for i in worker.get_products_completed_on_date(dd)]) for worker in Worker.objects.all()]
    #             }
    #         )
    #         data[-1]['contributions'].append(sum(data[-1]['contributions']))
    #         dd += timedelta(days=1)
    #     context['date_list'] = data
    #     d_list = [str(i) for i in d_list]
    #     print(str(d_list))
    #     x = [0]*len(data[0]['contributions'])
    #     from operator import add
    #     for i in data:
    #         x = list(map(add, x, i['contributions']))
    #     context['worker_total'] = x
    #     return context

class ProductDetailView(PermissionRequiredMixin, DetailView):
    model = Product
    permission_required = ('expert.view_product')

class WorkerListView(PermissionRequiredMixin, ListView):
    queryset = Worker.objects.filter(active=True).order_by('first_name')
    navigation = ''
    permission_required = ('expert.view_worker')

class WorkerCreateView(PermissionRequiredMixin, CreateView):
    model = Worker
    fields = [
        'first_name','last_name','_username','address',
        'date_joined','photo',
    ]
    template_name_suffix = '_create_form'
    permission_required = ('expert.view_worker','expert.add_worker')

    def form_valid(self, form):
        form.instance._username = form.instance._username.lower()
        return super().form_valid(form)

class WorkerDetailView(PermissionRequiredMixin, DetailView):
    model = Worker
    permission_required = ('expert.view_worker')

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
        return context

class WorkerUpdateView(PermissionRequiredMixin, UpdateView):
    model = Worker
    fields = [
        'first_name','last_name','_username','address',
        'date_joined','photo'
    ]
    template_name_suffix = '_update_form'
    permission_required = ('expert.view_worker','expert.change_worker')

    def form_valid(self, form):
        form.instance._username = form.instance._username.lower()
        return super().form_valid(form)

class WorkerDeleteView(PermissionRequiredMixin, DeleteView):
    model = Worker
    success_url = reverse_lazy('expert:worker-list')
    permission_required = ('expert.view_worker','expert.delete_worker')

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
        return HttpResponseRedirect(success_url)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class ChallanListView(PermissionRequiredMixin, ListView):
    model = Challan
    navigation = 'challan'
    ordering = ['-number']
    permission_required = ('expert.view_challan')

class ChallanDetailView(PermissionRequiredMixin, DetailView):
    model = Challan
    slug_field = 'number'
    permission_required = ('expert.view_challan','expert.view_product')

class ChallanPrintableView(PermissionRequiredMixin, DetailView):
    model = Challan
    slug_field = 'number'
    template_name_suffix = '_detail_printable'
    permission_required = ('expert.view_challan','expert.view_product')

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
    success_url = reverse_lazy('expert:challan-list')
    permission_required = ('expert.view_challan','expert.delete_challan')

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

class InvoiceCreateView(PermissionRequiredMixin, CreateView):
    model = Invoice
    fields = '__all__'
    template_name_suffix = '_create_form'
    permission_required = ('expert.view_invoice','expert.add_invoice')

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if Invoice.objects.all().exists():
            initial['number'] = Invoice.objects.all().order_by('-number').first().number + 1
        else:
            initial['number'] = 1
        initial['date_sent'] = datetime.now()
        initial['destination'] = 'Gandhinagar'
        initial['motor_vehicle_number'] = 'GJ-18-AU-3381'
        return initial

    def get_success_url(self):
        return self.object.get_absolute_url()

class InvoiceListView(PermissionRequiredMixin, ListView):
    model = Invoice
    navigation = 'invoice'
    ordering = ['-number']
    permission_required = ('expert.view_invoice')

class InvoiceDetailView(PermissionRequiredMixin, DetailView):
    model = Invoice
    slug_field = 'number'
    permission_required = ('expert.view_invoice','expert.view_challan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challan_list'] = Challan.objects.filter(invoice=None).order_by('-number')
        return context
    
class InvoiceChallanOperationView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Invoice
    pk_url_kwarg = 'invoice_pk'
    permission_required = ('expert.view_invoice','expert.view_challan','expert.change_invoice','expert.change_challan')

    def get_redirect_url(self, *args, **kwargs):
        invoice = self.get_object()
        if self.kwargs['operation'] == 'add':
            invoice.add_challan(self.kwargs['challan_pk'])
        else:
            invoice.remove_challan(self.kwargs['challan_pk'])
        return invoice.get_absolute_url()

class InvoicePrintableView(PermissionRequiredMixin, DetailView):
    model = Invoice
    slug_field = 'number'
    template_name_suffix = '_detail_printable'
    permission_required = ('expert.view_invoice','expert.view_challan')

    def get_context_date(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['challan_list'] = self.object.challans.order_by('number')
        return context

class InvoiceUpdateView(PermissionRequiredMixin, UpdateView):
    model = Invoice
    # fields = '__all__'
    form_class = InvoiceUpdateForm
    template_name_suffix = '_update_form'
    slug_field = 'number'
    permission_required = ('expert.view_invoice','expert.change_invoice')

    def form_valid(self, form):
        print(form.instance.number)
        return super().form_valid(form)

    def form_invalid(self, form):
        print('form is invalid')
        return super().form_invalid(form)