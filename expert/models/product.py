from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import date
from dateutil.relativedelta import relativedelta as timedelta

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
        return self.filter(status='completed')

    def returned(self):
        return self.filter(status='returned')

    def dispatched(self):
        return self.filter(dispatched=True)

    def remaining(self):
        return self.filter(dispatched=False)

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

    @property
    def value(self):
        if not self.exists():
            return 0
        return round(sum([i.value for i in self.all()]), 2)

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
    FABRIC_COST = {
        'max': 10.31,
        'tuff': 12.54,
        'fab': 0.0,
        'clear': 0.0,
    }
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
        'challan.Challan',
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_DEFAULT,
        related_name='products',
        help_text=_('Challan that this product is dispatched through')
    )
    assignedto = models.ForeignKey(
        'worker.Worker',
        on_delete=models.SET_DEFAULT,
        null=True,
        default=None,
        blank=True,
        related_name='products_assigned',
        verbose_name=_('Assigned To'),
        help_text=_('Worker that is assigned to this product'),
    )
    #TODO: change the on_delete so that worker is not deleted if 
    # there are no products completed.
    completedby = models.ForeignKey(
        'worker.Worker',
        on_delete=models.SET_DEFAULT,
        null=True,
        default=None,
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

    def assign(self, worker=None):
        if self.dispatched or worker is None:
            return False
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
        if self.is_dispatched and rr != 'fault' or self.is_returned and rr=='fault':
            # you cannot return a product with un/semi/mistake if product is already dispatched
            return False
        if rr != 'fault':
            self.uncomplete()
        self.return_remark = rr
        self.status = 'returned'
        self.save()
        return True

    def add_challan(self, challan=None):
        # challan = Challan.objects.get(id=challan_id)
        if self.is_dispatched or challan is None:
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
    def value(self):
        cost = self.FABRIC_COST[self.fabric]
        return round(cost * self.size, 2)

    @property
    def split_factors(self):
        if self.quantity == 1:
            return []
        ret = []
        a = 2
        while a<=self.quantity:
            if self.quantity%a==0:
                ret.append(a)
            a+=1
        return ret

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
        return reverse('expert:product-detail', kwargs={'pk':self.pk})

    def get_complete_url(self):
        return reverse('expert:product-complete', kwargs={'pk': self.pk})

    def get_uncomplete_url(self):
        return reverse('expert:product-uncomplete', kwargs={'pk': self.pk})