# Generated by Django 3.0.5 on 2020-05-21 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0061_auto_20200521_1038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kit',
            name='date_shipped',
        ),
        migrations.AddField(
            model_name='product',
            name='date_shipped',
            field=models.DateField(blank=True, help_text='Date at which Product is to be shipped to customer in format (YYYY-MM-DD).', null=True, verbose_name='Shipping Date'),
        ),
    ]
