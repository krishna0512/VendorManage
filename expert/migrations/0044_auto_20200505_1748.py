# Generated by Django 3.0.5 on 2020-05-05 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0043_auto_20200430_1542'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='worker',
            options={'permissions': [('view_profile', 'Worker can view thier own profile')]},
        ),
    ]