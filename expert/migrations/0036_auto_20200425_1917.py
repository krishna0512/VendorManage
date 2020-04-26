# Generated by Django 3.0.5 on 2020-04-25 13:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expert', '0035_auto_20200422_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='worker', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='worker',
            name='username',
            field=models.CharField(default='', help_text='Username for worker login (unique for each worker)', max_length=100, verbose_name='Username'),
        ),
    ]
