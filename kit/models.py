from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import date
from dateutil.relativedelta import relativedelta as timedelta

from product.models import Product

def kit_image_path(instance, filename):
    # return 'Kit_{}/Images/{}'.format(instance.number, filename)
    return 'Kit/{}/Images/{}'.format(instance.number, filename)

class KitQuerySet(models.QuerySet):
    def get_date_received_range(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date + timedelta(months=1) - timedelta(days=1)
        return self.filter(date_received__lte=end_date, date_received__gte=start_date)

    def products(self):
        # TODO: make some other representation so that we dont hve to import Product
        return Product.objects.filter(kit__in=self.all())

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
    date_return = models.DateField(
        # auto_now_add=True,
        null=True,
        blank=True,
        verbose_name=_('Expected Return Date'),
        help_text=_('Date at which KIT is expected to be returned in format (YYYY-MM-DD).'),
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

    objects = KitQuerySet.as_manager()

    def __repr__(self):
        return '<Kit: {}>'.format(str(self.number))

    def __str__(self):
        return str(self.number)

    @staticmethod
    def get_list_url():
        return reverse('kit:list')

    @staticmethod
    def get_create_url():
        return reverse('kit:create')

    def get_absolute_url(self):
        return reverse(
            'kit:detail',
            kwargs={
                'slug': self.number
            }
        )

    def get_update_url(self):
        return reverse('kit:update', kwargs={'slug': self.number})

    def get_delete_url(self):
        return reverse('kit:delete', kwargs={'slug': self.number})

    def get_uncomplete_url(self):
        return reverse('kit:uncomplete', kwargs={'pk': self.pk})

    def get_change_completion_date_url(self):
        return reverse('kit:change-completion-date', kwargs={'pk': self.pk})
    
    @staticmethod
    def get_all():
        return Kit.objects.all()

    @property
    def size(self):
        return self.products.all().size

    @property
    def quantity(self):
        return self.products.all().quantity

    # @property
    # def quantity_detail(self):
    #     # pending = sum([i.quantity for i in self.products.pending()])
    #     # completed = sum([i.quantity for i in self.products.completed()])
    #     # assigned = sum([i.quantity for i in self.products.assigned()])
    #     # returned = sum([i.quantity for i in self.products.returned()])
    #     # dispatched = sum([i.quantity for i in self.products.dispatched()])
    #     ret = {
    #         'pending': self.products.pending().quantity,
    #         'assigned': self.products.assigned().quantity,
    #         'completed': self.products.completed().dispatched().quantity,
    #         'returned': self.products.returned().dispatched().quantity,
    #         'dispatched': self.products.dispatched().quantity,
    #     }
    #     return ret

    # @property
    # def size_detail(self):
    #     # pending = sum([i.size for i in self.products.pending()])
    #     # completed = sum([i.size for i in self.products.completed()])
    #     # assigned = sum([i.size for i in self.products.assigned()])
    #     # returned = sum([i.size for i in self.products.returned()])
    #     # dispatched = sum([i.size for i in self.products.dispatched()])
    #     ret = {
    #         'pending': self.products.pending().size,
    #         'assigned': self.products.assigned().size,
    #         'completed': self.products.completed().dispatched().size,
    #         'returned': self.products.returned().dispatched().size,
    #         'dispatched': self.products.dispatched().size,
    #     }
    #     return ret