# Generated by Django 3.0.5 on 2020-04-06 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0026_product_return_remark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('completed', 'Completed'), ('dispatched', 'Dispatched'), ('returned', 'Returned')], default='pending', help_text='Status of the Product', max_length=50, verbose_name='Status'),
        ),
    ]
