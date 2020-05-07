from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import date

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
    invoice = models.ForeignKey(
        'Invoice',
        null=True,
        default=None,
        blank=True,
        related_name='challans',
        on_delete=models.CASCADE,
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

    def get_total_quantity(self):
        return sum([i.quantity for i in self.products.filter(return_remark='')])

    def get_total_size(self):
        # BUG: exclude the returned products from sum DONE
        return round(sum([i.size for i in self.products.filter(return_remark='')]),2)

    def get_total_size_by_fabric(self):
        ret = {}
        ret['max'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='max')]),2)
        ret['tuff'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='tuff')]),2)
        ret['fab'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='fab')]),2)
        ret['clear'] = round(sum([i.size for i in self.products.filter(return_remark='', fabric='clear')]),2)
        return ret

    def get_total_value(self):
        return round(self.get_total_size() * 3.5, 2)

    def get_return_quantity(self):
        return sum([i.quantity for i in self.products.exclude(return_remark='')])

    def get_return_size(self):
        # BUG: exclude the returned products from sum DONE
        return str(round(sum([i.size for i in self.products.exclude(return_remark='')]),2))

    def get_absolute_url(self):
        return reverse(
            'expert:challan-detail', kwargs={'slug': self.number}
        )

    def __str__(self):
        return '{} ({})'.format(self.number, self.date_sent)