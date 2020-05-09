# Generated by Django 3.0.5 on 2020-05-09 10:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('worker', '0001_initial'),
        ('expert', '0055_auto_20200509_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='assignedto',
            field=models.ForeignKey(blank=True, default=None, help_text='Worker that is assigned to this product', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products_assigned', to='worker.Worker', verbose_name='Assigned To'),
        ),
        migrations.AlterField(
            model_name='product',
            name='completedby',
            field=models.ForeignKey(blank=True, default=None, help_text='worker that completed this product', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products_completed', to='worker.Worker', verbose_name='Completed By'),
        ),
    ]