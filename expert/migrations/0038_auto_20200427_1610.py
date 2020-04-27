# Generated by Django 3.0.5 on 2020-04-27 10:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expert', '0037_auto_20200426_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='worker', to=settings.AUTH_USER_MODEL),
        ),
    ]