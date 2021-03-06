# Generated by Django 3.0.5 on 2020-05-06 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0047_auto_20200506_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challan',
            name='customer',
            field=models.ForeignKey(default=None, help_text='The customer for against whom challan is drawn', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='challans', to='expert.Customer'),
        ),
    ]
