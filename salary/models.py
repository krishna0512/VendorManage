from django.db import models
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from datetime import date
from dateutil.relativedelta import relativedelta as timedelta

# Create your models here.

class SalaryQuerySet(models.QuerySet):
    def active(self):
        pass

class Salary(models.Model):
    date_generated = models.DateField(
        auto_now_add=True,
    )
    worker = models.ForeignKey(
        'worker.Worker',
        on_delete=models.CASCADE,
        related_name='salaries',
    )
    date_from = models.DateField(
        verbose_name=_('From Date'),
    )
    date_to = models.DateField(
        verbose_name=_('To Date'),
    )
    _fixed_rate = models.DecimalField(
        default=0.0,
        max_digits=6,
        decimal_places=2,
        verbose_name=_('Daily Salary'),
        help_text=_('Total Daily salary (without decimal places)'),
    )
    _variable_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        # TODO: retrieve the default rate from settings.
        default=2.5,
        verbose_name=_('SqFt Rate'),
        help_text=_('Rate of the worker per Sq.Ft.'),
    )
    _amount = models.DecimalField(
        default=0.0,
        max_digits=7,
        decimal_places=2,
    )
    objects = SalaryQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('salary:detail', kwargs={'pk': self.pk})

    @staticmethod
    def get_list_url():
        return reverse('salary:list')

    @staticmethod
    def get_create_url():
        return reverse('salary:create')

    def products(self):
        return self.worker.products_completed.get_date_completed_range(self.date_from, self.date_to).order_by('date_completed')

    @property
    def amount(self):
        ret = 0
        if self.is_fixed:
            days = self.products().dates('date_completed', 'day').count()
            ret = days * self.fixed_rate
        else:
            cs = self.products().completed().size
            rs = self.products().returned().value
            ret = (cs * float(self.variable_rate)) - rs
        return round(ret, 2)

    def get_rate(self):
        if self.is_fixed:
            return '{} / Day'.format(self._fixed_rate)
        else:
            return '{} / Sq.Ft.'.format(self._variable_rate)

    @property
    def variable_rate(self):
        return self._variable_rate

    @property
    def fixed_rate(self):
        return self._fixed_rate

    @property
    def is_fixed(self):
        return self.fixed_rate != 0 and self.variable_rate == 0