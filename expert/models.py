from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class Product(models.Model):
    COLOR_CHOICES = [
        ('black','Black'),
        # account for biege
        ('beige','Beige'),
        ('blue','Blue'),
        ('white','White'),
        ('brown','Brown'),
        ('green','Green'),
        ('sand','Sand'),
        # account for burgandy
        ('burgundy','Burgundy'),
        # account for gray, grey
        ('gray','Gray'),
        ('clear','Clear'),

        ('olive_green','Olive Green'),
        ('light_sand','Light Sand'),
        # account for light gray, grey
        ('light_gray','Light Gray'),
        # account for coffee
        ('coffee_brown','Coffee Brown'),
    ]
    FABRIC_CHOICES = [
        ('max','Cover MAX'),
        ('tuff','Cover TUFF'),
        ('fab', 'Cover Fab'),
        ('clear', 'Cover Clear'),
    ]
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('assigned','Assigned'),
        ('completed','Completed'),
        # This status is for when product is added to challan and dispatched.
        ('dispatched','Dispatched'),
        ('returned','Returned'),
    ]
    RETURN_REMARK_CHOICES = [
        ('', ''),
        ('unprocessed', 'UnProcessed'),
        ('semiprocessed', 'Semi-Processed'),
        ('mistake', 'Cutting Mistake'),
    ]

    order_number = models.CharField(
        max_length=50,
        default='',
        blank=False,
        verbose_name=_('Order Number'),
        help_text=_('Number of order e.g. COV27622'),
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        verbose_name=_('Quantity (Pcs)'),
        help_text=_('Number of commissions'),
    )
    size = models.FloatField(
        default=0.0,
        blank=False,
        verbose_name=_('Size (Sq.Ft.)'),
        help_text=_('Total size of product in square feet.'),
    )
    fabric = models.CharField(
        max_length=10,
        choices=FABRIC_CHOICES,
        help_text=_('Fabric to be used to complete order.'),
    )
    color = models.CharField(
        max_length=50,
        choices=COLOR_CHOICES,
        default='black',
        verbose_name=_('Color'),
        help_text=_('Color of the lot.'),
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status'),
        help_text=_('Status of the Product'),
    )
    kit = models.ForeignKey(
        'Kit',
        on_delete=models.CASCADE,
        related_name='products',
        help_text=_('Kit that this product belongs to.'),
    )
    challan = models.ForeignKey(
        'Challan',
        null=True,
        default=None,
        blank=True,
        on_delete=models.CASCADE,
        related_name='products',
        help_text=_('Challan that this product is dispatched through')
    )
    assignedto = models.ForeignKey(
        'Worker',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='products_assigned',
        verbose_name=_('Assigned To'),
        help_text=_('Worker that is assigned to this product'),
    )
    #TODO: change the on_delete so that worker is not deleted if 
    # there are no products completed.
    completedby = models.ForeignKey(
        'Worker',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='products_completed',
        verbose_name=_('Completed By'),
        help_text=_('worker that completed this product'),
    )
    # TODO: add validators so that this date is always >= kit start date
    date_completed = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of Completion'),
        help_text=_('Date at which worker completed with this product in format (YYYY-MM-DD)'),
    )
    #TODO: change the status of the product if return_remark is changed in updateView?
    return_remark = models.CharField(
        max_length=200,
        choices=RETURN_REMARK_CHOICES,
        blank=True,
        default='',
        verbose_name=_('Return Remarks'),
        help_text=_('Select the appropriate remark for returned products'),
    )
    creation_timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    def __repr__(self):
        return '<Product: {} ({})>'.format(self.order_number, self.id)

    # TODO: update the str and repr definations
    def __str__(self):
        return str(self.order_number)

    def save(self, *args, **kwargs):
        # BUG: This should be removed and added to the views.py in appropriate form.
        self.order_number = self.order_number.upper()
        self.size = round(self.size, 2)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'expert:product-detail', kwargs={'pk':self.id}
        )

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

    def add_challan(self, challan_pk):
        """ function to add a challan to self invoice and perform various calculations.
        """
        challan = Challan.objects.get(id=challan_pk)
        challan.invoice = self
        challan.save()
        self.save()

    def remove_challan(self, challan_pk):
        """ function to remove the given challan from invoice 
        return False if challan is not present in this invoice.
        """
        challan = Challan.objects.get(id=challan_pk)
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
        ret['total_words'] = 'xxxxxxxxxxxxxxxxxxxxxxx'
        return ret

    def get_total_amount(self):
        ret = {}
        ret['amount'] = int(self.get_total_tax()['total'] + self.get_total_tax()['roundoff'] + self.get_total_value())
        ret['words'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        return ret

    def get_total_size_by_fabric(self):
        ret = {'max':0, 'tuff':0, 'fab':0, 'clear':0}
        for c in self.challans.all():
            for i in c.get_total_size_by_fabric():
                ret[i] += c.get_total_size_by_fabric()[i]
        return ret

    def get_absolute_url(self):
        return reverse('expert:invoice-detail', kwargs={'slug': self.number})

    def __str__(self):
        return self.number

    def __repr__(self):
        return '<Invoice: {}>'.format(self.number)

def kit_image_path(instance, filename):
    # return 'Kit_{}/Images/{}'.format(instance.number, filename)
    return 'Kit/{}/Images/{}'.format(instance.number, filename)

class Kit(models.Model):
    """Container for model that represents the KIT that is sent each day"""
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('working','Working'),
        ('completed','Completed'),
        ('dispatched','Dispatched'),
    ]

    number = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        unique=True,
        verbose_name=_('Kit Number'),
        help_text=_('Unique number of kit from delivery challan.'),
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status'),
        help_text=_('Status of the Kit'),
    )
    date_received = models.DateField(
        # auto_now_add=True,
        null=True,
        blank=True,
        verbose_name=_('Date Received'),
        help_text=_('Date at which KIT is received in format (YYYY-MM-DD).'),
    )
    date_product_completion = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Product Completion Date'),
        help_text=_('Manual Date which can be set so that all the products \
            in this kit will be completed on this date')
    )
    data = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Excel Data'),
        help_text=_('Copy paste the excel rows containing the product data'),
    )
    original_kit_summary = models.ImageField(
        upload_to=kit_image_path,
        null=True,
        blank=True,
        verbose_name=_('Original KIT Image'),
        help_text=_('Upload the jpg of the original/unmodified image of kit summary'),
    )
    jobwork_challan = models.ImageField(
        upload_to=kit_image_path,
        null=True,
        blank=True,
        verbose_name=_('Jobwork Challan Image'),
        help_text=_('Upload the jpg/png image of the jobwork challan that came with kit.'),
    )
    ewaybill = models.ImageField(
        upload_to=kit_image_path,
        null=True,
        blank=True,
        verbose_name=_('E-Way Bill'),
        help_text=_('GSTN E-Way Bill that came with the kit'),
    )
    jobwork_gatepass = models.ImageField(
        upload_to=kit_image_path,
        null=True,
        blank=True,
        verbose_name=_('Jobwork Gate Pass'),
        help_text=_('Upload the original jpg/png of the jobwork gatepass that came with kit'),
    )

    def __repr__(self):
        return '<Kit: {}>'.format(str(self.number))

    def __str__(self):
        return str(self.number)

    def get_absolute_url(self):
        return reverse(
            'expert:kit-detail',
            kwargs={
                'slug': self.number
            }
        )

    def get_total_size(self):
        return round(sum([i.size for i in self.products.all()]),2)

    def get_total_quantity(self):
        return sum([i.quantity for i in self.products.all()])

    def get_pending_quantity(self):
        return sum([i.quantity for i in self.products.filter(status='pending')])

    def cleanup(self):
        if self.original_kit_summary:
            self.original_kit_summary.delete(False)
        if self.jobwork_challan:
            self.jobwork_challan.delete(False)
        if self.jobwork_gatepass:
            self.jobwork_gatepass.delete(False)
        if self.ewaybill:
            self.ewaybill.delete(False)


def worker_image_path(instance, filename):
    return 'Worker/{}/{}'.format(instance.first_name.lower(), filename)

class Worker(models.Model):
    first_name = models.CharField(
        max_length=100,
        default='',
        blank=False,
    )
    last_name = models.CharField(
        max_length=100,
        default='',
        blank=True,
    )
    address = models.TextField(
        default='',
        blank=True,
        help_text=_('Full Address of the worker.'),
    )
    date_joined = models.DateField(
        null=True,
        blank=False,
        verbose_name=_('Joined since'),
        help_text=_('Date of joining.'),
    )
    photo = models.ImageField(
        upload_to=worker_image_path,
        null=True,
        blank=True,
        help_text=_('Passport size profile picture for worker.'),
    )
    active = models.BooleanField(
        default=True,
        blank=False,
        verbose_name=_('Is Active?'),
        help_text=_('Is the Worker Active?'),
    )

    def get_fullname(self):
        if self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            return self.first_name

    def get_total_contribution(self):
        return round(sum([i.size for i in self.products_completed.all()]),2)

    def get_approx_contribution_badge(self):
        x = self.get_total_contribution()
        if x == 0:
            return 'nil'
        elif x>0 and x<100:
            return '{}+'.format(str(int(x/10)*10))
        elif x>=100 and x<1000:
            return '{}+'.format(str(int(x/100)*100))
        elif x>=1000:
            return '{}+'.format(str(int(x/1000)*1000))

    def get_products_completed_on_date(self, date):
        """Returns all the products completed by this worker on
        a prticular date given.
        """
        return self.products_completed.all().filter(date_completed=date)

    def __repr__(self):
        return '<Worker: {}>'.format(self.first_name.lower())

    def __str__(self):
        return self.get_fullname()

    def get_absolute_url(self):
        return reverse(
            'expert:worker-detail',
            kwargs={
                'pk': self.id
            }
        )

    def cleanup(self):
        if self.photo:
            self.photo.delete(False)
