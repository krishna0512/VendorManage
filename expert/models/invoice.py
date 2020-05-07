from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from num2words import num2words
from datetime import date

class Invoice(models.Model):
    number = models.IntegerField(
        blank=False,
        unique=True,
        verbose_name=_('Invoice Number'),
        help_text=_('Unique number of each delivery invoice'),
    )
    date_sent = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('Date of Dispatch'),
        help_text=_('Date at which this invoice was created and dispatched')
    )
    # TODO: add a validator for vNo
    motor_vehicle_number = models.CharField(
        blank=False,
        null=False,
        default='',
        max_length=100,
        verbose_name=_('Motor Vehicle No.'),
        help_text=_('Vehicle number from which the invoice is dispatched'),
    )
    destination = models.CharField(
        blank=False,
        null=False,
        default='',
        max_length=100,
        help_text=_('Detination to which this invoice is dispatched'),
    )

    def add_challan(self, challan):
        """ function to add a challan to self invoice and perform various calculations.
        """
        # TODO: check for the condition if new challan added
        # should have the same customer as the already added challans
        challan.invoice = self
        challan.save()
        self.save()

    def remove_challan(self, challan):
        """ function to remove the given challan from invoice 
        return False if challan is not present in this invoice.
        """
        challan.invoice = None
        challan.save()
        self.save()

    def get_total_quantity(self):
        return sum([i.get_total_quantity() for i in self.challans.all()])

    def get_total_size(self):
        return round(sum([i.get_total_size() for i in self.challans.all()]),2)

    def get_total_value(self):
        return round(self.get_total_size() * 3.5,2)

    def get_total_tax(self):
        ret = {}
        ret['cgst'] = round(self.get_total_value() * 0.06, 2)
        ret['sgst'] = ret['cgst']
        ret['total'] = ret['cgst'] + ret['sgst']
        t = ret['total'] + self.get_total_value()
        x = t*100//1%100
        if x<50:
            x = round(x/100, 2)
            x = -x
        else:
            x = 100 - x
            x = round(x/100, 2)
        ret['roundoff'] = x
        ret['total_words'] = '{} rupees and {} paise'.format(num2words(int(ret['total'])), num2words(int(ret['total']*100)%100))
        return ret

    def get_total_amount(self):
        ret = {}
        ret['amount'] = int(self.get_total_tax()['total'] + self.get_total_tax()['roundoff'] + self.get_total_value())
        ret['words'] = num2words(ret['amount'], lang='en_IN')
        return ret

    def get_total_size_by_fabric(self):
        ret = {'max':0, 'tuff':0, 'fab':0, 'clear':0}
        for c in self.challans.all():
            for i in c.get_total_size_by_fabric():
                ret[i] += c.get_total_size_by_fabric()[i]
        for i in ret:
            ret[i] = round(ret[i], 2)
        return ret

    def get_absolute_url(self):
        return reverse('expert:invoice-detail', kwargs={'slug': self.number})

    def __str__(self):
        return self.number

    def __repr__(self):
        return '<Invoice: {}>'.format(self.number)