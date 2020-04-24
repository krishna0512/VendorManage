# Generated by Django 3.0.5 on 2020-04-13 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0032_auto_20200408_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='destination',
            field=models.CharField(default='', help_text='Detination to which this invoice is dispatched', max_length=100),
        ),
        migrations.AddField(
            model_name='invoice',
            name='motor_vehicle_number',
            field=models.CharField(default='', help_text='Vehicle number from which the invoice is dispatched', max_length=100, verbose_name='Motor Vehicle No.'),
        ),
    ]