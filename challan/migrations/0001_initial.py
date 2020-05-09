# Generated by Django 3.0.5 on 2020-05-09 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Challan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(help_text='Unique number of each delivery challan', unique=True, verbose_name='Challan Number')),
                ('date_sent', models.DateField(help_text='Date at which this challan is dispatched', null=True, verbose_name='Date of Dispatch')),
                ('customer', models.ForeignKey(default=None, help_text='The customer for against whom challan is drawn', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='challans', to='customer.Customer')),
                ('invoice', models.ForeignKey(blank=True, default=None, help_text='The Invoice to which this challan belongs to', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='challans', to='invoice.Invoice')),
            ],
        ),
    ]