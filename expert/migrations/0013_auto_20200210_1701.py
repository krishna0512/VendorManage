# Generated by Django 3.0.3 on 2020-02-10 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0012_auto_20200210_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='assignedto',
            field=models.ForeignKey(blank=True, help_text='worker that completed this product', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products_assigned', to='expert.Worker', verbose_name='Assigned To'),
        ),
        migrations.AlterField(
            model_name='product',
            name='completedby',
            field=models.ForeignKey(blank=True, help_text='worker that completed this product', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products_completed', to='expert.Worker', verbose_name='Completed By'),
        ),
    ]
