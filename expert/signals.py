from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from .models import Kit, Product, Order, Worker

@receiver(post_delete)
def all_cleanup_files(sender, instance, **kwargs):
    if 'cleanup' in dir(instance):
        instance.cleanup()
