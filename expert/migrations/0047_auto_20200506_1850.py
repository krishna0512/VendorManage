# Generated by Django 3.0.5 on 2020-05-06 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0046_challan_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='address1',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Address Line 1'),
        ),
        migrations.AddField(
            model_name='customer',
            name='address2',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Address Line 2'),
        ),
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='customer',
            name='gstn',
            field=models.CharField(blank=True, default='N/A', help_text='GST Number of the customer', max_length=18, verbose_name='GSTN'),
        ),
        migrations.AddField(
            model_name='customer',
            name='iec',
            field=models.CharField(blank=True, default='N/A', help_text='IEC Number of the customer as included in Challan', max_length=20, verbose_name='IEC'),
        ),
    ]
