from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.dates import MonthArchiveView, DayArchiveView

from expert.models import Kit, Product, Worker

# Create your views here.

class IndexTemplateView(TemplateView):
    template_name='expert/index.html'

class KitListView(ListView):
    model = Kit

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
        data = data.strip().split('\n')
        for row in data:
            r = row.strip().split('\t')
            r = [i.strip() for i in r]
            Product.objects.create(
                order_number=r[0],
                quantity=int(r[1]),
                size=float(r[2]),
                fabric=r[3].split()[1].lower(),
                color=r[4].lower(),
                kit=self.object,
            )

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.data:
            self.process_excel_data(self.object.data)
        return response

class KitUpdateView(UpdateView):
    model = Kit
    fields = '__all__'
    template_name_suffix = '_update_form'

class KitDetailView(DetailView):
    model = Kit
    slug_field = 'number'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['worker_list'] = Worker.objects.all()
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

class ProductCreateView(CreateView):
    model = Product
    fields = '__all__'
    template_name_suffix = '_create_form'

def product_complete(request, pk):
    #TODO: change the p to product and convert to Class based view
    p = Product.objects.get(id=pk)
    p.completedby = p.assignedto
    p.status = 'completed'
    p.date_completed = datetime.now()
    p.save()
    return redirect(p.kit.get_absolute_url())

def product_assign(request, product_pk, worker_pk):
    # Convert to class based RedirectView 
    product = Product.objects.get(id=product_pk)
    worker = Worker.objects.get(id=worker_pk)
    product.assignedto = worker
    product.status = 'assigned'
    product.save()
    return redirect(product.kit.get_absolute_url())

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
    template_name_suffix = '_report_day'

    def get_context_data(self, *args, **kwargs):
        worker_list = []
        context = super().get_context_data(*args, **kwargs)
        for worker in Worker.objects.all():
            p = Product.objects.filter(completedby=worker).filter(date_completed=context['day'])
            ret = {}
            ret['name'] = worker.get_fullname()
            if p.exists():
                ret['daily_work'] = sum([i.size for i in p])
            else:
                ret['daily_work'] = 0.0
            worker_list.append(ret)
        context['worker_list'] = worker_list
        return context

class ProductMonthArchiveView(MonthArchiveView):
    model = Product
    date_field = 'date_completed'
    allow_empty = True
    allow_future = True
    template_name_suffix = '_report_month'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        print(context['month'])
        print(context['next_month'])
        start_date = context['month']
        end_date = context['next_month'] - timedelta(days=1)
        ret = []
        x = []
        x.append('Day')
        x += [i.get_fullname() for i in Worker.objects.all()]
        ret.append(x)
        dd = start_date
        while dd <= end_date:
            x = [dd]
            for worker in Worker.objects.all():
                r = worker.get_products_completed_on_date(dd)
                if not r.exists():
                    x.append(0)
                else:
                    r = sum([i.size for i in r])
                    x.append(r)
            ret.append(x)
            dd += timedelta(days=1)
        context['data'] = ret
        return context

class WorkerListView(ListView):
    model = Worker

class WorkerCreateView(CreateView):
    model = Worker
    fields = '__all__'
    template_name_suffix = '_create_form'

class WorkerDetailView(DetailView):
    model = Worker