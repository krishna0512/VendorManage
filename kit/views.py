from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from datetime import datetime, date

from expert.models import Product
from .models import Kit
from worker.models import Worker

class KitListView(PermissionRequiredMixin, ListView):
    model = Kit
    # for navigation active display
    navigation = 'kit'
    ordering = ['-number']
    permission_required = ('kit.view_kit')

class KitCreateView(PermissionRequiredMixin, CreateView):
    model = Kit
    fields = '__all__'
    template_name_suffix = '_create_form'
    permission_required = ('kit.view_kit','kit.add_kit')

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

        def _get_date(date, year_string='%Y'):
            ret = None
            try:
                ret = datetime.strptime(date, '%d-%b-{}'.format(year_string)).date()
            except:
                ret = datetime.strptime(date, '%d-%B-{}'.format(year_string)).date()
            return ret

        data = data.strip().split('\n')
        date_received = date_return = None
        for row in data:
            r = row.strip().split('\t')
            r = [i.strip() for i in r]
            Product.objects.create(
                order_number=r[0].upper(),
                date_shipped=_get_date(r[2], year_string='%y'),
                name=r[3],
                quantity=int(r[4]),
                size=float(r[5]),
                fabric=_select_fabric(r[6]),
                color=_select_color(r[7]),
                kit=self.object,
            )
            date_received = _get_date(r[8])
            date_return = _get_date(r[9])
        self.object.date_received = date_received
        self.object.date_return = date_return
        self.object.save()

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
    permission_required = ('kit.view_kit','kit.change_kit')

class KitDetailView(PermissionRequiredMixin, DetailView, MultipleObjectMixin):
    model = Kit
    slug_field = 'number'
    paginate_by = 10
    # template_name_suffix = '_detail_react'
    permission_required = ('kit.view_kit','expert.view_product')

    def get(self, *args, **kwargs):
        self.paginate_by = self.request.GET.get('paginate_by', 10) or 10
        return super().get(*args, **kwargs)

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
        tpq = object_list.quantity
        tps = object_list.size
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['worker_list'] = worker_list
        context['product_list'] = context['object_list']
        context['total_product_size'] = tps
        context['total_product_quantity'] = tpq
        return context

class KitDeleteView(PermissionRequiredMixin, DeleteView):
    model = Kit
    slug_field = 'number'
    success_url = reverse_lazy('kit:list')
    permission_required = ('kit.view_kit','kit.delete_kit')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class KitUncompleteRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Kit
    permission_required = ('kit.view_kit','expert.view_product','expert.change_product',)

    def get_redirect_url(self, *args, **kwargs):
        kit = self.get_object()
        for product in kit.products.all():
            product.uncomplete()
        return kit.get_absolute_url()

@method_decorator(csrf_exempt, name='dispatch')
class KitChangeCompletionDate(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Kit
    http_method_names = ['post']
    permission_required = ('kit.view_kit','expert.view_product','kit.change_kit',)

    def post(self, *args, **kwargs):
        kit = self.get_object()
        date = self.request.POST.get('date',None)
        date = datetime.strptime(date, '%Y-%m-%d').date()
        kit.date_product_completion = date
        kit.save()
        return JsonResponse({'date': date.strftime('%B %d, %Y')})