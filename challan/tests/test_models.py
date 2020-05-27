from django.test import TestCase
from django.urls import reverse

from invoice.models import Invoice
from challan.models import Challan
from customer.models import Customer

class ChallanModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Challan.objects.create(number=10)

    def setUp(self):
        self.challan = Challan.objects.get(number=10)
    
    def test_field_number(self):
        field = self.challan._meta.get_field('number')
        self.assertEqual(field.verbose_name, 'Challan Number')
        self.assertTrue(field.unique)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_field_date_sent(self):
        field = self.challan._meta.get_field('date_sent')
        self.assertEqual(field.verbose_name, 'Date of Dispatch')
        self.assertTrue(field.null)
        self.assertFalse(field.blank)