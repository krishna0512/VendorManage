# Generated by Django 3.0.5 on 2020-04-04 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expert', '0019_product_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kit',
            name='date_received',
            field=models.DateField(blank=True, help_text='Date at which KIT is received in format (YYYY-MM-DD).', null=True, verbose_name='Date Received'),
        ),
        migrations.AlterField(
            model_name='product',
            name='color',
            field=models.CharField(choices=[('black', 'Black'), ('beige', 'Beige'), ('blue', 'Blue'), ('white', 'White'), ('brown', 'Brown'), ('green', 'Green'), ('olive green', 'Olive Green'), ('light', 'Light'), ('coffee brown', 'Coffee Brown'), ('sand', 'Sand'), ('burgundy', 'Burgundy'), ('gray', 'Gray')], default='black', help_text='Color of the lot.', max_length=50, verbose_name='Color'),
        ),
    ]
