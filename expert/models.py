from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from num2words import num2words
from datetime import datetime, date
from dateutil.relativedelta import relativedelta as timedelta
# Create your models here.

class ProductQuerySet(models.QuerySet):
    def get_date_completed_range(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + timedelta(months=1) - timedelta(days=1)
        return self.filter(date_completed__lte=end_date, date_completed__gte=start_date)

    def pending(self):
        return self.filter(status='pending')

    def assigned(self):
        return self.filter(status='assigned')

    def completed(self):
        """This filters the products that are already dispatched"""
        return self.filter(status='completed')

    def returned(self):
        return self.filter(status='returned')

    def dispatched(self):
        return self.filter(dispatched=True)

    @property
    def quantity(self):
        """returns the sum of quantity of the products in filter"""
        if not self.exists():
            return 0
        return sum([i.quantity for i in self.all()])

    @property
    def size(self):
        """returns the sum of the size of the products in filter (rounded 2)"""
        if not self.exists():
            return 0.0
        return round(sum([i.size for i in self.all()]), 2)

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
        ('fault', 'Fault'),
    ]

    class Meta:
        permissions = [
            ('assign_product','Can Assign a worker to product'),
            ('complete_product','Can Complete a product'),
        ]
    objects = ProductQuerySet.as_manager()

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
    _size = models.FloatField(
        default=0.0,
        blank=False,
        verbose_name=_('Size (Sq.Ft.)'),
        help_text=_('Total size of product in square feet.'),
    )
    fabric = models.CharField(
        max_length=10,
        choices=FABRIC_CHOICES,
        verbose_name=_('Fabric'),
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
    dispatched = models.BooleanField(default=False)
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

    def __str__(self):
        return str(self.order_number)

    def save(self, *args, **kwargs):
        # BUG: This should be removed and added to the views.py in appropriate form.
        self.order_number = self.order_number.upper()
        self.size = round(self.size, 2)
        return super().save(*args, **kwargs)

    def assign(self, worker_id):
        if self.dispatched:
            return False
        worker = Worker.objects.get(id=worker_id)
        self.assignedto = worker
        self.completedby = None
        self.date_completed = None
        self.return_remark = ''
        self.status = 'assigned'
        self.save()
        return True

    def complete(self):
        """TODO: refactor the method to use Exceptions"""
        if not self.assignedto or (self.kit.date_product_completion and self.kit.date_product_completion > date.today()):
            return False
        if not self.is_assigned:
            return False
        self.completedby = self.assignedto
        if self.kit.date_product_completion:
            self.date_completed = self.kit.date_product_completion
        else:
            self.date_completed = date.today()
        self.status = 'completed'
        self.save()
        return True

    def uncomplete(self):
        if self.is_dispatched or not self.is_completed:
            return False
        self.completedby = None
        self.date_completed = None
        self.status = 'assigned'
        self.save()
        return True

    def return_product(self, rr=None):
        if rr is None or rr not in ['unprocessed','semiprocessed','mistake','fault']:
            return False
        if self.is_dispatched and rr != 'fault':
            # you cannot return a product with un/semi/mistake if product is already dispatched
            return False
        self.return_remark = rr
        self.status = 'returned'
        self.save()
        return True

    def add_challan(self, challan_id):
        challan = Challan.objects.get(id=challan_id)
        if self.is_dispatched:
            return False
        if not self.is_completed and not self.is_returned:
            return False
        self.challan = challan
        self.dispatched = True
        self.save()
        return True

    def remove_challan(self):
        if not self.is_dispatched:
            return False
        self.challan = None
        self.dispatched = False
        self.save()
        return True

    @property
    def size(self):
        return round(self._size, 2)
    @size.setter
    def size(self, value):
        if value < 0:
            raise ValueError("Size cannot be negative")
        self._size = round(value, 2)

    @property
    def is_pending(self):
        return self.status == 'pending'
    @property
    def is_assigned(self):
        return self.status == 'assigned'
    @property
    def is_completed(self):
        return self.status == 'completed'
    @property
    def is_returned(self):
        return self.status == 'returned'
    @property
    def is_dispatched(self):
        return self.dispatched

    def get_absolute_url(self):
        return reverse('expert:product-detail', kwargs={'pk':self.id})

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

def kit_image_path(instance, filename):
    # return 'Kit_{}/Images/{}'.format(instance.number, filename)
    return 'Kit/{}/Images/{}'.format(instance.number, filename)

class KitQuerySet(models.QuerySet):
    def get_date_received_range(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + timedelta(months=1) - timedelta(days=1)
        return self.filter(date_received__lte=end_date, date_received__gte=start_date)

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
    jobwork_gatepass_processed = models.ImageField(
        upload_to=kit_image_path,
        null=True,
        blank=True,
        verbose_name=_('Jobwork GatePass (Processed)'),
        help_text=_('The field for storing the gate pass after it is processed')
    )

    objects = KitQuerySet.as_manager()

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

    @property
    def size(self):
        return round(sum([i.size for i in self.products.all()]), 2)

    @property
    def quantity(self):
        return sum([i.quantity for i in self.products.all()])

    @property
    def quantity_detail(self):
        # pending = sum([i.quantity for i in self.products.pending()])
        # completed = sum([i.quantity for i in self.products.completed()])
        # assigned = sum([i.quantity for i in self.products.assigned()])
        # returned = sum([i.quantity for i in self.products.returned()])
        # dispatched = sum([i.quantity for i in self.products.dispatched()])
        ret = {
            'pending': self.products.pending().quantity,
            'assigned': self.products.assigned().quantity,
            'completed': self.products.completed().dispatched().quantity,
            'returned': self.products.returned().dispatched().quantity,
            'dispatched': self.products.dispatched().quantity,
        }
        return ret

    @property
    def size_detail(self):
        # pending = sum([i.size for i in self.products.pending()])
        # completed = sum([i.size for i in self.products.completed()])
        # assigned = sum([i.size for i in self.products.assigned()])
        # returned = sum([i.size for i in self.products.returned()])
        # dispatched = sum([i.size for i in self.products.dispatched()])
        ret = {
            'pending': self.products.pending().size,
            'assigned': self.products.assigned().size,
            'completed': self.products.completed().dispatched().size,
            'returned': self.products.returned().dispatched().size,
            'dispatched': self.products.dispatched().size,
        }
        return ret

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

class WorkerQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

class Worker(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='worker',
        blank=True,
        null=True,
    )
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
    _username = models.CharField(
        max_length=100,
        verbose_name=_('Username'),
        default='',
        help_text=_('Username for worker login (unique for each worker)'),
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
    # TODO: check if you can retrieve the image of aadhar from aadhar number
    aadhar_number = models.CharField(
        default='',
        blank=True,
        max_length=12,
        verbose_name=_('Aadhar #'),
        help_text=_('Aadhar number of the worker registered. (Enter without any space or delimiter)')
    )
    # TODO: do proper validations for both aadhar and mobile number
    mobile_number = models.CharField(
        default='',
        blank=True,
        max_length=20,
        verbose_name=_('Mobile #'),
        help_text=('10-digit mobile number of the worker without leading zero(s)'),
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

    objects = WorkerQuerySet.as_manager()

    @property
    def fullname(self):
        if self.last_name:
            return '{} {}'.format(self.first_name.capitalize(), self.last_name.capitalize())
        else:
            return self.first_name.capitalize()

    @property
    def username(self):
        return self._username.strip().capitalize()

    @username.setter
    def username(self, value):
        if self.user:
            self.user.username = value.lower()
            self.user.save()
        self._username = value.lower()

    def get_date_completed_product_range(self, start_date, end_date=None):
        """Get all the products completed by the worker between these dates."""
        if end_date is None:
            end_date = start_date + timedelta(months=1) - timedelta(days=1)
        kit_list = Kit.objects.get_date_received_range(start_date, end_date)
        ret = Product.objects.filter(completedby=self, kit__in=kit_list)
        return ret

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
        return self.fullname

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


from expert.signals import *