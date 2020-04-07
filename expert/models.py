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

    def get_total_quantity(self):
        return sum([i.quantity for i in self.products.filter(return_remark='')])

    def get_total_size(self):
        # BUG: exclude the returned products from sum DONE
        return str(round(sum([i.size for i in self.products.filter(return_remark='')]),2))

    def get_return_quantity(self):
        return sum([i.quantity for i in self.products.exclude(return_remark='')])

    def get_return_size(self):
        # BUG: exclude the returned products from sum DONE
        return str(round(sum([i.size for i in self.products.exclude(return_remark='')]),2))

    def get_absolute_url(self):
        return reverse(
            'expert:challan-detail', kwargs={'slug': self.number}
        )


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
        return str(round(sum([i.size for i in self.products.all()]),2))

    def get_total_quantity(self):
        return sum([i.quantity for i in self.products.all()])

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
