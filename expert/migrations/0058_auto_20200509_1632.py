# Generated by Django 3.0.5 on 2020-05-09 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0057_auto_20200509_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='challan',
            field=models.IntegerField(blank=True, default=None, help_text='Challan that this product is dispatched through', null=True),
        ),
        migrations.DeleteModel(
            name='Challan',
        ),
    ]