# Generated by Django 3.0.5 on 2020-04-18 17:03

from django.db import migrations, models
import expert.models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0033_auto_20200413_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='kit',
            name='jobwork_gatepass_processed',
            field=models.ImageField(blank=True, help_text='The field for storing the gate pass after it is processed', null=True, upload_to=expert.models.kit_image_path, verbose_name='Jobwork GatePass (Processed)'),
        ),
    ]