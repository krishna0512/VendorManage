# Generated by Django 3.0.3 on 2020-02-10 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0009_auto_20200210_0607'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.RemoveField(
            model_name='product',
            name='number',
        ),
    ]
