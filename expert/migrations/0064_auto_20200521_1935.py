# Generated by Django 3.0.5 on 2020-05-21 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0063_auto_20200521_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('completed', 'Completed'), ('returned', 'Returned')], default='pending', help_text='Status of the Product', max_length=50, verbose_name='Status'),
        ),
    ]
