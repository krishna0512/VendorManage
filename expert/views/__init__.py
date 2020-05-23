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
from django.conf import settings

from expert.models import Product, Challan
from kit.models import Kit
from worker.models import Worker
from invoice.models import Invoice
from expert.forms import *
from helper.mail import Mail

import sendgrid
from sendgrid.helpers import mail
from tempfile import TemporaryDirectory
import os
import logging
logger = logging.getLogger(__name__)

# Create your views here.

class IndexTemplateView(LoginRequiredMixin, TemplateView):
    template_name='expert/index.html'

@csrf_exempt
def complaint_detail(request):
    n = int(request.POST.get('ctype', 0))
    kit_id = str(request.POST.get('kit_list', 0))
    kit = None
    try:
        kit = Kit.objects.get(id=kit_id)
    except Exception:
        pass
    challan = None
    try:
        challan_id = str(request.POST.get('challan_list', 0))
        challan = Challan.objects.get(id=challan_id)
    except Exception:
        pass
    to = []
    subject = ''
    message = ''
    pnumber = str(request.POST.get('product_number', ''))
    pqty = str(request.POST.get('product_qty', ''))
    psize = str(request.POST.get('product_size', ''))
    pcolor = str(request.POST.get('product_color', ''))
    if n==1 and kit:
        to += ['expertcovers2020@gmail.com', 'anjutulsyan19@gmail.com']
        subject = "Short Receipt of Materials"
        message = ''.join([
            "Dear Sir,\n\n",
            "In Ref to Kit no: {} dated {}, for {} pcs totaling {} Sq.Ft.\n".format(
                kit.number,
                kit.date_received.strftime('%d/%m/%Y'),
                kit.products.all().quantity,
                kit.products.all().size,
            ),
            "We have not received {} pcs of {} color Order no. {} for {} Sq.ft.\n".format(
                pqty,
                pcolor.capitalize(),
                pnumber.upper(),
                psize,
            ),
            "We acknowledge the receipt of {} Pcs for {} Sq.Ft.\n\n".format(
                kit.products.all().quantity - int(pqty if pqty else 0),
                kit.products.all().size - float(psize if psize else 0),
            ),
            "Regards,\n",
            "Vinayak Tulsyan"
        ])
    elif n==2 and challan:
        to += ['kt.krishna.tulsyan@gmail.com', 'anjutulsyan19@gmail.com']
        subject = 'Challan Delivery Report'
        message = ''.join([
            'Dear Shailash Bhai,\n\n',
            'Attached is the latest copy of the challan sent for details given below as delivered to bharat bhai:\n',
            'Date - {}\n'.format(challan.date_sent.strftime('%d/%m/%Y')),
            'Challan No - {}\n'.format(challan.number),
            'Challan Qty - {}\n'.format(challan.products.all().quantity),
            'Challan Size - {}\n\n'.format(challan.products.all().size),
            'Thanks & Regards,\nVinayak Tulsyan'
        ])
    return JsonResponse({
        'to': to,
        'subject': subject,
        'message': message,
    })

class SendEmailView(RedirectView):

    def get_redirect_url(self):
        m = Mail(
            to=[
                ('kt.krishna.tulsyan@gmail.com', 'Krishna Tulsyan'),
            ],
            subject=self.request.POST.get('subject', ''),
            message=self.request.POST.get('message', ''),
        )
        if 'challan_pdf' in self.request.FILES:
            m.add_attachment(self.request.FILES['challan_pdf'])
        m.send()
        return reverse('expert:index')

class ProductDayArchiveView(DayArchiveView):
    model = Product
    date_field = 'date_completed'
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
        context['worker_list'] = Worker.objects.all()
        return context

class ProductMonthArchiveView(PermissionRequiredMixin, MonthArchiveView):
    model = Product
    date_field = 'date_completed'
    allow_empty = True
    allow_future = True
    permission_required = ('only_superuser')
    template_name_suffix = '_report_month'

    def has_permission(self):
        """Only allow the access to this page is the user is a superuser."""
        return self.request.user.is_superuser or self.request.user.username=='demo'

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
        context['total_product_completed'] = kit_list.products().dispatched().completed().size
        context['total_product_returned'] = kit_list.products().dispatched().returned().size
        context['total_product_received'] = kit_list.products().size
        context['total_product_dispatched'] = kit_list.products().dispatched().size
        context['average_qty_product'] = round(kit_list.products().size / kit_list.products().count(), 2)
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
        context['chart_data'] = chart_data
        return context