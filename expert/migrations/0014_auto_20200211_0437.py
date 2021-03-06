# Generated by Django 3.0.3 on 2020-02-11 04:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0013_auto_20200210_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='assignedto',
            field=models.ForeignKey(blank=True, help_text='Worker that is assigned to this product', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products_assigned', to='expert.Worker', verbose_name='Assigned To'),
        ),
    ]
