from django.db import models
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from datetime import date
from dateutil.relativedelta import relativedelta as timedelta

from expert.models import Kit, Product

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

    class Meta:
        permissions = [
            ('view_profile', 'Worker can view thier own profile'),
        ]
    objects = WorkerQuerySet.as_manager()

    @property
    def fullname(self):
        if self.last_name:
            return '{} {}'.format(self.first_name.capitalize(), self.last_name.capitalize())
        else:
            return self.first_name.capitalize()

    @property
    def username(self):
        return self._username.strip().capitalize() if self._username else ''

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
        # TODO: figure out something without having to import kit and products
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
        return reverse('worker:detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('worker:update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('worker:delete', kwargs={'pk': self.pk})

    @staticmethod
    def get_list_url():
        return reverse('worker:list')

    @staticmethod
    def get_create_url():
        return reverse('worker:create')

    def cleanup(self):
        if self.photo:
            self.photo.delete(False)

@receiver(post_save, sender=Worker)
def create_user_for_worker(sender, instance, created, **kwargs):
    # If the user is not defined for the worker and you
    # have included the username in worker then create&update the user.
    if not instance.user and instance.username:
        u = User.objects.create(username=instance.username.lower())
        u.set_password(settings.WORKER_PASSWORD)
        g = Group.objects.get(name='BaseWorkers')
        u.groups.add(g)
        u.save()
        instance.user = u
        instance.save()
    # check for changes in username
    # This Functionality is redundant because of property getter and setters.
    # if instance.username != instance.user.username:
    #     u = instance.user
    #     u.username = instance.username
    #     u.save()