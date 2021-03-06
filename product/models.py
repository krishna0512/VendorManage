from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import date
from dateutil.relativedelta import relativedelta as timedelta

class ProductQuerySet(models.QuerySet):
    def get_date_completed_range(self, start_date, end_date=None):
        if isinstance(start_date, str) or isinstance(end_date, str):
            raise TypeError('start_date and end_date should be of type datetime.date object')
        if end_date is None:
            end_date = start_date + timedelta(months=1) - timedelta(days=1)
        return self.filter(date_completed__lte=end_date, date_completed__gte=start_date)

    def pending(self, **kwargs):
        return self.filter(status='pending').filter(**kwargs)

    def assigned(self, **kwargs):
        return self.filter(status='assigned').filter(**kwargs)

    def completed(self, **kwargs):
        return self.filter(status='completed').filter(**kwargs)

    def returned(self, **kwargs):
        return self.filter(status='returned').filter(**kwargs)

    def dispatched(self, **kwargs):
        return self.filter(dispatched=True).filter(**kwargs)

    def remaining(self, **kwargs):
        return self.filter(dispatched=False).filter(**kwargs)

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
        ('returned','Returned'),
    ]
    RETURN_REMARK_CHOICES = [
        ('', ''),
        ('unprocessed', 'UnProcessed'),
        ('semiprocessed', 'Semi-Processed'),
        ('mistake', 'Cutting Mistake'),
        ('damaged', 'Damaged Goods'),
        ('reject','Rejected'),
        ('rework', 'Re-Worked'),
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
    name = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name=_('Product Name'),
        help_text=_('Verbose product name as received from supervisor'),
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
        'kit.Kit',
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
    date_shipped = models.DateField(
        # auto_now_add=True,
        null=True,
        blank=True,
        verbose_name=_('Shipping Date'),
        help_text=_('Date at which Product is to be shipped to customer in format (YYYY-MM-DD).'),
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
    remark = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name=_('Remark'),
        help_text=_('Additional remark for the Product')
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
        if self.is_dispatched or worker is None:
            return False
        self.assignedto = worker
        self.completedby = None
        self.date_completed = None
        self.return_remark = ''
        self.status = 'assigned'
        self.save()
        return True

    def unassign(self):
        if self.is_assigned:
            self.assignedto = None
            self.status = 'pending'
            self.save()
            return True
        return False

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

    def return_product(self, rr=None) -> bool:
        if rr is None or rr not in [i[0] for i in self.RETURN_REMARK_CHOICES]:
            # checking if the input value of rr is valid
            return False
        if self.is_dispatched and rr not in ['reject','rework']:
            # you cannot return a product with un/semi/mistake if product is already dispatched
            return False
        if rr in ['unprocessed','semiprocessed','mistake','damaged']:
            # these return categories are worker independent (i.e. we dnt need the worker
            # infor for these categores) so we uncomplete the product.
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
        return reverse('product:detail', kwargs={'pk':self.pk})

    def get_update_url(self):
        return reverse('product:update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('product:delete', kwargs={'pk': self.pk})

    def get_complete_url(self):
        return reverse('expert:product-complete', kwargs={'pk': self.pk})

    def get_uncomplete_url(self):
        return reverse('expert:product-uncomplete', kwargs={'pk': self.pk})

    def get_return_url(self):
        return reverse('product:return', kwargs={'pk': self.pk})

    def get_split_url(self):
        return reverse('product:split', kwargs={'pk': self.pk})

    def get_api_url(self):
        return reverse('product:api-detail', kwargs={'pk': self.pk})

    def get_assign_url(self):
        return reverse('product:api-assign', kwargs={'pk': self.pk})