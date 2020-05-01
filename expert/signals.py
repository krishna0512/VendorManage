from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

from .models import Kit, Product, Worker

@receiver(post_delete)
def all_cleanup_files(sender, instance, **kwargs):
    if 'cleanup' in dir(instance):
        instance.cleanup()

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