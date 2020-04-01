# Generated by Django 3.0.3 on 2020-02-10 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0011_auto_20200210_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kit',
            name='date_received',
            field=models.DateField(auto_now_add=True, help_text='Date at which KIT is received in format (YYYY-MM-DD).', verbose_name='Date Received'),
        ),
        migrations.AlterField(
            model_name='kit',
            name='date_sent',
            field=models.DateField(blank=True, help_text='Date at which KIT is completed and dispatched in format (YYYY-MM-DD).', null=True, verbose_name='Date dispatched'),
        ),
        migrations.AlterField(
            model_name='product',
            name='completeddate',
            field=models.DateField(blank=True, help_text='Date at which worker completed with this product in format (YYYY-MM-DD)', null=True, verbose_name='Date of Completion'),
        ),
    ]
