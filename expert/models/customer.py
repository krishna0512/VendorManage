from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import date

class Customer(models.Model):
    name = models.CharField(
        max_length=100,
        default='',
        verbose_name=_('Name'),
        help_text=_('Name of the company or Individual')
    )
    address1 = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name=_('Address Line 1'),
    )
    address2 = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name=_('Address Line 2'),
    )
    email = models.EmailField(
        max_length=100,
        default='',
        blank=True,
    )
    gstn = models.CharField(
        max_length=18,
        default='N/A',
        blank=True,
        verbose_name=_('GSTN'),
        help_text=_('GST Number of the customer'),
    )
    iec = models.CharField(
        max_length=20,
        default='N/A',
        blank=True,
        verbose_name=_('IEC'),
        help_text=_('IEC Number of the customer as included in Challan'),
    )
    default = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('expert:customer-detail', kwargs={'pk':self.id})

    def __str__(self):
        return self.name.capitalize()