# Generated by Django 3.0.5 on 2020-04-29 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0040_auto_20200428_2225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='size',
            new_name='_size',
        ),
    ]
