# Generated by Django 3.0.5 on 2020-06-03 06:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('challan', '0004_auto_20200526_1956'),
        ('worker', '0006_worker_date_left'),
        ('kit', '0002_remove_kit_jobwork_gatepass_processed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(default='', help_text='Number of order e.g. COV27622', max_length=50, verbose_name='Order Number')),
                ('name', models.CharField(blank=True, default='', help_text='Verbose product name as received from supervisor', max_length=200, verbose_name='Product Name')),
                ('quantity', models.PositiveSmallIntegerField(default=1, help_text='Number of commissions', verbose_name='Quantity (Pcs)')),
                ('_size', models.FloatField(default=0.0, help_text='Total size of product in square feet.', verbose_name='Size (Sq.Ft.)')),
                ('fabric', models.CharField(choices=[('max', 'Cover MAX'), ('tuff', 'Cover TUFF'), ('fab', 'Cover Fab'), ('clear', 'Cover Clear')], help_text='Fabric to be used to complete order.', max_length=10, verbose_name='Fabric')),
                ('color', models.CharField(choices=[('black', 'Black'), ('beige', 'Beige'), ('blue', 'Blue'), ('white', 'White'), ('brown', 'Brown'), ('green', 'Green'), ('sand', 'Sand'), ('burgundy', 'Burgundy'), ('gray', 'Gray'), ('clear', 'Clear'), ('olive_green', 'Olive Green'), ('light_sand', 'Light Sand'), ('light_gray', 'Light Gray'), ('coffee_brown', 'Coffee Brown')], default='black', help_text='Color of the lot.', max_length=50, verbose_name='Color')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('completed', 'Completed'), ('returned', 'Returned')], default='pending', help_text='Status of the Product', max_length=50, verbose_name='Status')),
                ('dispatched', models.BooleanField(default=False)),
                ('date_completed', models.DateField(blank=True, help_text='Date at which worker completed with this product in format (YYYY-MM-DD)', null=True, verbose_name='Date of Completion')),
                ('date_shipped', models.DateField(blank=True, help_text='Date at which Product is to be shipped to customer in format (YYYY-MM-DD).', null=True, verbose_name='Shipping Date')),
                ('return_remark', models.CharField(blank=True, choices=[('', ''), ('unprocessed', 'UnProcessed'), ('semiprocessed', 'Semi-Processed'), ('mistake', 'Cutting Mistake'), ('damaged', 'Damaged Goods'), ('reject', 'Rejected'), ('rework', 'Re-Worked'), ('fault', 'Fault')], default='', help_text='Select the appropriate remark for returned products', max_length=200, verbose_name='Return Remarks')),
                ('remark', models.CharField(blank=True, default='', help_text='Additional remark for the Product', max_length=300, verbose_name='Remark')),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True)),
                ('assignedto', models.ForeignKey(blank=True, default=None, help_text='Worker that is assigned to this product', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products_assigned', to='worker.Worker', verbose_name='Assigned To')),
                ('challan', models.ForeignKey(blank=True, default=None, help_text='Challan that this product is dispatched through', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products', to='challan.Challan')),
                ('completedby', models.ForeignKey(blank=True, default=None, help_text='worker that completed this product', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='products_completed', to='worker.Worker', verbose_name='Completed By')),
                ('kit', models.ForeignKey(help_text='Kit that this product belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='products', to='kit.Kit')),
            ],
            options={
                'permissions': [('assign_product', 'Can Assign a worker to product'), ('complete_product', 'Can Complete a product')],
            },
        ),
    ]
