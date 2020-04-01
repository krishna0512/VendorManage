# Generated by Django 3.0.3 on 2020-02-08 13:01

from django.db import migrations, models
import expert.models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0007_auto_20200206_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='kit',
            name='ewaybill',
            field=models.ImageField(blank=True, help_text='GSTN E-Way Bill that came with the kit', null=True, upload_to=expert.models.kit_image_path, verbose_name='E-Way Bill'),
        ),
        migrations.AddField(
            model_name='kit',
            name='jobwork_challan',
            field=models.ImageField(blank=True, help_text='Upload the jpg/png image of the jobwork challan that came with kit.', null=True, upload_to=expert.models.kit_image_path, verbose_name='Jobwork Challan Image'),
        ),
        migrations.AddField(
            model_name='kit',
            name='jobwork_gatepass',
            field=models.ImageField(blank=True, help_text='Upload the original jpg/png of the jobwork gatepass that came with kit', null=True, upload_to=expert.models.kit_image_path, verbose_name='Jobwork Gate Pass'),
        ),
        migrations.AddField(
            model_name='worker',
            name='photo',
            field=models.ImageField(blank=True, help_text='Passport size profile picture for worker.', null=True, upload_to=expert.models.worker_image_path),
        ),
        migrations.AlterField(
            model_name='kit',
            name='number',
            field=models.PositiveSmallIntegerField(default=1, help_text='Unique number of kit from delivery challan.', unique=True, verbose_name='Kit Number'),
        ),
    ]
