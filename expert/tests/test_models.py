from django.test import TestCase
from django.contrib.auth.models import User
import django.db.models.fields as models
from datetime import datetime, date
from dateutil.relativedelta import relativedelta as timedelta

from expert.models import Worker, Product
from kit.models import Kit

class KitModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Kit.objects.create()
        Worker.objects.create()
    
    def setUp(self):
        self.kit = Kit.objects.get(id=1)
        self.worker = Worker.objects.get(id=1)
    
    def test_defaults(self):
        self.assertEqual(self.kit.number, 1)
        self.assertEqual(self.kit.status, 'pending')
        self.assertIsNone(self.kit.date_received)
        self.assertIsNone(self.kit.date_product_completion)
        self.assertEqual(self.kit.data, '')

    def test_status_choices(self):
        self.assertEqual(len(self.kit.STATUS_CHOICES), 4)
        self.assertEqual(self.kit.STATUS_CHOICES[0], ('pending','Pending'))
        self.assertEqual(self.kit.STATUS_CHOICES[1], ('working','Working'))
        self.assertEqual(self.kit.STATUS_CHOICES[2], ('completed','Completed'))
        self.assertEqual(self.kit.STATUS_CHOICES[3], ('dispatched','Dispatched'))

    def test_status_max_length(self):
        ml = self.kit._meta.get_field('status').max_length
        self.assertEqual(ml, 50)

    # def test_number_unique(self):
    #     from django.db.utils import IntegrityError
    #     self.assertRaises(IntegrityError, Kit.objects.create(number=1))

    def test_field_instances(self):
        self.assertIsInstance(self.kit._meta.get_field('number'), models.PositiveSmallIntegerField)
        self.assertIsInstance(self.kit._meta.get_field('status'), models.CharField)
        self.assertIsInstance(self.kit._meta.get_field('date_received'), models.DateField)
        self.assertIsInstance(self.kit._meta.get_field('date_product_completion'), models.DateField)
        self.assertIsInstance(self.kit._meta.get_field('data'), models.TextField)

    def test_property_size(self):
        self.assertEqual(self.kit.size, 0)
        self.kit.products.create(size=1.43263)
        self.assertEqual(self.kit.size, 1.43)
        self.kit.products.create(size=1.57)
        self.assertEqual(self.kit.size, 3.0)

    def test_property_quantity(self):
        self.assertEqual(self.kit.quantity, 0)
        self.kit.products.create(quantity=9)
        self.assertEqual(self.kit.quantity, 9)

    def test_property_quantity_detail(self):
        d = {'completed':0,'returned':0,'dispatched':0,'assigned':0,'pending':0}
        self.assertEqual(self.kit.quantity_detail, d)
        self.kit.products.create(quantity=3)
        d['pending'] = 3
        self.assertEqual(self.kit.quantity_detail, d)
        self.kit.products.all()[0].assign(self.worker.id)
        d['pending'] = 0
        d['assigned'] = 3
        self.assertEqual(self.kit.quantity_detail, d)
        self.kit.products.all()[0].complete()
        d['assigned'] = 0
        d['completed'] = 3
        self.assertEqual(self.kit.quantity_detail, d)
        self.kit.products.all()[0].return_product('mistake')
        d['completed'] = 0
        d['returned'] = 3
        self.assertEqual(self.kit.quantity_detail, d)
        p = self.kit.products.all()[0]
        p.dispatched = True
        p.save()
        self.kit.products.create(quantity=8)
        d['pending'] = 8
        d['dispatched'] = 3
        self.assertEqual(self.kit.quantity_detail, d)