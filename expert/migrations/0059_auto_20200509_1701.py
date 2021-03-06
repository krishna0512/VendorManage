# Generated by Django 3.0.5 on 2020-05-09 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challan', '0001_initial'),
        ('expert', '0058_auto_20200509_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='challan',
            field=models.ForeignKey(blank=True, default=None, help_text='Challan that this product is dispatched through', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products', to='challan.Challan'),
        ),
    ]
