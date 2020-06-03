from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import date

from product.models import Product

def challan_image_path(instance, filename):
    return 'Challan/{}/Images/{}'.format(instance.pk, filename)

class ChallanQuerySet(models.QuerySet):
    def products(self):
        return Product.objects.filter(challan__in=self.all())

    @property
    def quantity(self):
        return sum([i.quantity for i in self.all()])

    @property
    def size(self):
        return round(sum([i.size for i in self.all()]), 2)

    @property
    def value(self):
        return round(sum([i.value for i in self.all()]), 2)

class Challan(models.Model):
    """Container for model that represents Delivery Challan"""
    number = models.IntegerField(
        blank=False,
        unique=True,
        verbose_name=_('Challan Number'),
        help_text=_('Unique number of each delivery challan'),
    )
    date_sent = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('Date of Dispatch'),
        help_text=_('Date at which this challan is dispatched')
    )
    jobwork_gatepass_processed = models.ImageField(
        upload_to=challan_image_path,
        null=True,
        blank=True,
        verbose_name=_('Jobwork GatePass (Processed)'),
        help_text=_('The field for storing the gate pass after it is processed')
    )
    invoice = models.ForeignKey(
        'invoice.Invoice',
        null=True,
        default=None,
        blank=True,
        related_name='challans',
        on_delete=models.SET_DEFAULT,
        help_text=_('The Invoice to which this challan belongs to')
    )
    customer = models.ForeignKey(
        'customer.Customer',
        related_name='challans',
        on_delete=models.SET_DEFAULT,
        null=True,
        default=None,
        help_text=_('The customer for against whom challan is drawn'),
    )

    objects = ChallanQuerySet.as_manager()

    class Meta:
        ordering = ('-number',)

    @staticmethod
    def get_all():
        return Challan.objects.all()

    @property
    def quantity(self):
        return self.products.all().completed().quantity

    @property
    def size(self):
        return self.products.all().completed().size

    @property
    def value(self):
        return round(self.size * 3.5, 2)

    @property
    def return_quantity(self):
        return self.products.all().returned().quantity

    @property
    def return_size(self):
        return self.products.all().returned().size

    # def get_total_quantity(self):
    #     return sum([i.quantity for i in self.products.filter(return_remark='')])

    # def get_total_size(self):
    #     # BUG: exclude the returned products from sum DONE
    #     return round(sum([i.size for i in self.products.filter(return_remark='')]),2)

    def get_total_size_by_fabric(self):
        # ret = {}
        ret = {
            'max': self.products.completed(fabric='max').size,
            'tuff': self.products.completed(fabric='tuff').size,
            'fab': self.products.completed(fabric='fab').size,
            'clear': self.products.completed(fabric='clear').size,
        }
        # ret['max'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='max')]),2)
        # ret['tuff'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='tuff')]),2)
        # ret['fab'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='fab')]),2)
        # ret['clear'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='clear')]),2)
        return ret

    # def get_total_value(self):
    #     return round(self.size * 3.5, 2)

    # def get_return_quantity(self):
    #     return sum([i.quantity for i in self.products.exclude(return_remark='')])

    # def get_return_size(self):
    #     # BUG: exclude the returned products from sum DONE
    #     return str(round(sum([i.size for i in self.products.exclude(return_remark='')]),2))

    def get_absolute_url(self):
        return reverse('challan:detail', kwargs={'slug': self.number})

    def get_excel_url(self):
        return reverse('challan:excel', kwargs={'pk': self.pk})

    def get_printable_url(self):
        return reverse('challan:printable', kwargs={'slug': self.number})

    def get_delete_url(self):
        return reverse('challan:delete', kwargs={'slug': self.number})

    def get_update_url(self):
        return reverse('challan:update', kwargs={'pk': self.pk})
    
    @staticmethod
    def get_list_url():
        return reverse('challan:list')

    def __str__(self):
        return '{} ({})'.format(self.number, self.date_sent)