from datetime import date
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from expert.models import Kit, Product
from worker.models import Worker
from expert.forms import *

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
    success_url = reverse_lazy('expert:kit-list')
    permission_required = ('expert.view_kit','expert.delete_kit')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class KitUncompleteRedirectView(PermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Kit
    permission_required = ('expert.view_kit','expert.view_product','expert.change_product',)

    def get_redirect_url(self, *args, **kwargs):
        kit = self.get_object()
        for product in kit.products.all():
            product.uncomplete()
        return kit.get_absolute_url()