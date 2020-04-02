from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class Product(models.Model):
    COLOR_CHOICES = [
        ('black','Black'),
        ('biege','Biege'),
        ('white','White'),
        ('brown','Brown'),
        ('gray','Gray'),
    ]
    FABRIC_CHOICES = [
        ('max','Cover MAX'),
        ('tuff','Cover TUFF'),
    ]

    order_number = models.CharField(
        max_length=50,
        default='',
        blank=False,
        verbose_name=_('Order Number'),
        help_text=_('Unique number of order e.g. COV27622'),
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
    kit = models.ForeignKey(
        'Kit',
        on_delete=models.CASCADE,
        related_name='products',
        help_text=_('Kit that this product belongs to.'),
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

    def __repr__(self):
        return '<Product: {}>'.format(self.order_number)

    # TODO: update the str and repr definations
    def __str__(self):
        return str(self.order_number)

    def save(self, *args, **kwargs):
        self.order_number = self.order_number.upper()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.kit.get_absolute_url()


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
        auto_now_add=True,
        verbose_name=_('Date Received'),
        help_text=_('Date at which KIT is received in format (YYYY-MM-DD).'),
    )
    date_sent = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date dispatched'),
        help_text=_('Date at which KIT is completed and dispatched in format (YYYY-MM-DD).'),
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

    def cleanup(self):
        if self.original_kit_summary:
            self.original_kit_summary.delete(False)


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

    def get_fullname(self):
        if self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            return self.first_name

    def get_total_contribution(self):
        return 0.0

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
