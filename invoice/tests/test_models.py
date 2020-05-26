from django.test import TestCase
from django.urls import reverse

from invoice.models import Invoice
from challan.models import Challan
from customer.models import Customer

class InvoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Invoice.objects.create(number=1)
        Customer.objects.create(name='customer1')
        Customer.objects.create(name='customer2')
        for i in range(10):
            Challan.objects.create(number=i+1, customer=Customer.objects.get(id=1))
        for i in range(10):
            Challan.objects.create(number=i+11, customer=Customer.objects.get(id=2))

    def setUp(self):
        self.invoice = Invoice.objects.get(id=1)
    
    def test_field_number(self):
        field = self.invoice._meta.get_field('number')
        self.assertEqual(field.verbose_name, 'Invoice Number')
        self.assertTrue(field.unique)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_field_date_sent(self):
        field = self.invoice._meta.get_field('date_sent')
        self.assertEqual(field.verbose_name, 'Date of Dispatch')
        self.assertTrue(field.null)
        self.assertFalse(field.blank)

    def test_field_motor_vehicle_number(self):
        field = self.invoice._meta.get_field('motor_vehicle_number')
        self.assertEqual(field.verbose_name, 'Motor Vehicle No.')
        self.assertEqual(field.default, '')
        self.assertEqual(field.max_length, 100)
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_field_destination(self):
        field = self.invoice._meta.get_field('destination')
        # self.assertEqual(field.verbose_name, 'Destination')
        self.assertEqual(field.max_length, 100)
        self.assertEqual(field.default, '')
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_str(self):
        self.assertEqual(self.invoice.__str__(), str(self.invoice.number))

    def test_repr(self):
        self.assertEqual(self.invoice.__repr__(), '<Invoice: 1>')

    def test_list_url(self):
        self.assertEqual(Invoice.get_list_url(), reverse('invoice:list'))

    def test_create_url(self):
        self.assertEqual(Invoice.get_create_url(), reverse('invoice:create'))

    def test_absolute_url(self):
        self.assertEqual(
            self.invoice.get_absolute_url(),
            reverse('invoice:detail', kwargs={'slug': self.invoice.number})
        )

    def test_update_url(self):
        self.assertEqual(
            self.invoice.get_update_url(),
            reverse('invoice:update', kwargs={'slug': self.invoice.number})
        )

    def test_printable_url(self):
        self.assertEqual(
            self.invoice.get_printable_url(),
            reverse('invoice:printable', kwargs={'slug': self.invoice.number})
        )

    def test_add_challan(self):
        c1 = Challan.objects.get(number=5)
        c2 = Challan.objects.get(number=10)
        c3 = Challan.objects.get(number=15)
        self.assertTrue(self.invoice.add_challan(c1))
        self.assertEqual(self.invoice.challans.all().count(), 1)
        self.assertTrue(self.invoice.add_challan(c2))
        self.assertEqual(self.invoice.challans.all().count(), 2)
        self.assertFalse(self.invoice.add_challan(c3))
        self.assertEqual(self.invoice.challans.all().count(), 2)
        c = Challan.objects.create(number=100)
        self.assertFalse(self.invoice.add_challan(c))
        self.assertEquals(self.invoice.challans.all().count(), 2)

    def test_remove_challan(self):
        c = Challan.objects.get(number=6)
        self.assertFalse(self.invoice.remove_challan(c))
        for i in Challan.objects.filter(number__lte=5):
            self.invoice.add_challan(i)
        self.assertEqual(self.invoice.challans.all().count(), 5)
        c = Challan.objects.get(number=6)
        self.assertFalse(self.invoice.remove_challan(c))
        self.assertEqual(self.invoice.challans.all().count(), 5)
        c = Challan.objects.get(number=4)
        self.assertTrue(self.invoice.remove_challan(c))
        self.assertEqual(self.invoice.challans.all().count(), 4)
        self.assertNotIn(4, self.invoice.challans.all().values_list('number', flat=True))