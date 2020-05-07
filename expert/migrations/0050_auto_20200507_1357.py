# Generated by Django 3.0.5 on 2020-05-07 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
        ('expert', '0049_customer_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challan',
            name='customer',
            field=models.ForeignKey(default=None, help_text='The customer for against whom challan is drawn', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='challans', to='customer.Customer'),
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
    ]
