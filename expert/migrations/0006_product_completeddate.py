# Generated by Django 3.0.3 on 2020-02-05 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0005_auto_20200205_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='completeddate',
            field=models.DateField(blank=True, help_text='Date at which worker completed with this product', null=True, verbose_name='Date of Completion'),
        ),
    ]
