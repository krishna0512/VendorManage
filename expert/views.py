from datetime import datetime, timedelta
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.dates import MonthArchiveView, DayArchiveView
from django.views.decorators.csrf import csrf_exempt

from expert.models import Kit, Product, Worker, Challan, Invoice
from expert.forms import *

# Create your views here.

class IndexTemplateView(TemplateView):
    template_name='expert/index.html'

class KitListView(ListView):
    model = Kit
    # for navigation active display
    navigation = 'kit'
    ordering = ['-number']

class KitCreateView(CreateView):
    model = Kit
    fields = '__all__'
    template_name_suffix = '_create_form'

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if Kit.objects.all().exists():
            n = max([i.number for i in Kit.objects.all()])+1
        else:
            n = 1
        initial['number'] = str(n)
        initial['date_received'] = datetime.now()
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

class KitUpdateView(UpdateView):
    model = Kit
    slug_field = 'number'
    fields = [
        'number','date_product_completion'
    ]
    template_name_suffix = '_update_form'

class KitDetailView(DetailView):
    model = Kit
    slug_field = 'number'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['worker_list'] = Worker.objects.filter(active=True)
        context['product_list'] = self.object.products.all().order_by('id')
        return context

class KitDeleteView(DeleteView):
    model = Kit
    slug_field = 'number'
    success_url = reverse_lazy('expert:kit-list')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class ProductUpdateView(UpdateView):
    model = Product
    fields = '__all__'
    template_name_suffix = '_update_form'

    def form_valid(self, form):
        if form.instance.return_remark:
            form.instance.status = 'returned'
        return super().form_valid(form)

class ProductCreateView(CreateView):
    model = Product
    fields = [
        'order_number','quantity','size',
        'fabric','color','status','assignedto',
        'completedby','date_completed','return_remark'
    ]
    template_name_suffix = '_create_form'

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
        form.instance.kit = Kit.objects.filter(number=self.kwargs['kit_number']).first()
        return super().form_valid(form)

@csrf_exempt
def product_complete(request, pk):
    #TODO: change the p to product and convert to Class based view
    product = Product.objects.get(id=pk)
    product.completedby = product.assignedto
    if product.kit.date_product_completion:
        product.date_completed = product.kit.date_product_completion
    else:
        product.date_completed = datetime.now()
    product.status = 'completed'
    product.save()
    return JsonResponse({'saved': True})

@csrf_exempt
def product_assign(request, product_pk, worker_pk):
    # Convert to class based RedirectView 
    product = Product.objects.get(id=product_pk)
    worker = Worker.objects.get(id=worker_pk)
    product.assignedto = worker
    product.return_remark = ''
    product.status = 'assigned'
    product.save()
    return JsonResponse({'assignedto': worker.get_fullname()})

def product_return(request, pk):
    product =  Product.objects.get(id=pk)
    rr = request.GET.get('rr', None)
    if rr in ['unprocessed','semiprocessed','mistake']:
        product.return_remark = str(rr)
        product.status = 'returned'
        product.save()
    return redirect(product.get_absolute_url())

# TODO: add a function in product model for completeing and uncompleting the product
def kit_uncomplete(request, pk):
    kit = Kit.objects.get(id=pk)
    products = kit.products.filter(status='completed')
    for product in products:
        product.completedby = None
        product.date_completed = None
        product.status = 'assigned'
        product.save()
    return redirect(kit.get_absolute_url())


def challan_init(request, pk):
    def _get_challan_number():
        if not Challan.objects.all().exists():
            return 51
        else:
            return Challan.objects.all().order_by('-number').first().number + 1
    kit = Kit.objects.get(id=pk)
    challan = Challan.objects.create(
        date_sent=datetime.now(),
        number=_get_challan_number(),
    )
    products = kit.products.filter(status='completed') | kit.products.filter(status='returned')
    for product in products:
        product.challan = challan
        product.status = 'dispatched'
        product.save()
    challan.date_sent = max([i.date_completed for i in challan.products.all() if i.date_completed])
    challan.save()
    return redirect(kit.get_absolute_url())

class ProductDeleteView(DeleteView):
    model = Product

    def delete(self, request, *args, **kwargs):
        self.kit_number = self.get_object().kit.number
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return Kit.objects.filter(number=self.kit_number).first().get_absolute_url()

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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['worker_list'] = Worker.objects.all().order_by('first_name')
        start_date = context['month']
        end_date = context['next_month'] - timedelta(days=1)
        data = []
        dd = start_date
        while dd <= end_date:
            data.append(
                {
                    'date': dd,
                    'contributions': [sum([i.size for i in worker.get_products_completed_on_date(dd)]) for worker in Worker.objects.all()]
                }
            )
            data[-1]['contributions'].append(sum(data[-1]['contributions']))
            dd += timedelta(days=1)
        context['date_list'] = data
        x = [0]*len(data[0]['contributions'])
        from operator import add
        for i in data:
            x = list(map(add, x, i['contributions']))
        context['worker_total'] = x
        return context

class ProductDetailView(DetailView):
    model = Product

class WorkerListView(ListView):
    queryset = Worker.objects.filter(active=True).order_by('first_name')
    navigation = ''

class WorkerCreateView(CreateView):
    model = Worker
    fields = [
        'first_name','last_name','address',
        'date_joined','photo',
    ]
    template_name_suffix = '_create_form'

class WorkerDetailView(DetailView):
    model = Worker

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

class WorkerUpdateView(UpdateView):
    model = Worker
    fields = [
        'first_name','last_name','address',
        'date_joined','photo'
    ]
    template_name_suffix = '_update_form'

class WorkerDeleteView(DeleteView):
    model = Worker
    success_url = reverse_lazy('expert:worker-list')

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

class ChallanListView(ListView):
    model = Challan
    navigation = 'challan'
    ordering = ['-number']

class ChallanDetailView(DetailView):
    model = Challan
    slug_field = 'number'

class ChallanPrintableView(DetailView):
    model = Challan
    slug_field = 'number'
    template_name_suffix = '_detail_printable'

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

class ChallanDeleteView(DeleteView):
    model = Challan
    slug_field = 'number'
    success_url = reverse_lazy('expert:challan-list')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        for product in self.object.products.all():
            # TODO: I shouldnt have to reset the challan foreign key
            # it should be done automatically but todo that we have to most probably change
            # the on_delete attrib of challan in Product to somethingelse instead of CASCADE
            product.challan = None
            if product.status == 'dispatched':
                product.status = 'returned' if product.return_remark else 'completed'
            product.save()
        return super().delete(request, *args, **kwargs)
        # success_url = self.get_success_url()
        # self.object.active = False
        # self.object.save()
        # return HttpResponseRedirect(success_url)

class InvoiceCreateView(CreateView):
    model = Invoice
    fields = '__all__'
    template_name_suffix = '_create_form'

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if Invoice.objects.all().exists():
            initial['number'] = Invoice.objects.all().order_by('-number').first().number + 1
        else:
            initial['number'] = 1
        initial['date_sent'] = datetime.now()
        return initial

    def get_success_url(self):
        return self.object.get_absolute_url()

class InvoiceListView(ListView):
    model = Invoice
    navigation = 'invoice'
    ordering = ['-number']

class InvoiceDetailView(DetailView):
    model = Invoice
    slug_field = 'number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challan_list'] = Challan.objects.filter(invoice=None).order_by('-number')
        return context
    

def invoice_add_challan(request, invoice_pk, challan_pk):
    invoice = Invoice.objects.get(id=invoice_pk)
    invoice.add_challan(challan_pk)
    return redirect(invoice.get_absolute_url())

def invoice_remove_challan(request, invoice_pk, challan_pk):
    invoice = Invoice.objects.get(id=invoice_pk)
    invoice.remove_challan(challan_pk)
    print('removed the challan from invoice')
    return redirect(invoice.get_absolute_url())

class InvoicePrintableView(DetailView):
    model = Invoice
    slug_field = 'number'
    template_name_suffix = '_detail_printable'

    def get_context_date(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['challan_list'] = self.object.challans.order_by('number')
        return context

class InvoiceUpdateView(UpdateView):
    model = Invoice
    # fields = '__all__'
    form_class = InvoiceUpdateForm
    template_name_suffix = '_update_form'
    slug_field = 'number'

    def form_valid(self, form):
        print(form.instance.number)
        return super().form_valid(form)

    def form_invalid(self, form):
        print('form is invalid')
        return super().form_invalid(form)