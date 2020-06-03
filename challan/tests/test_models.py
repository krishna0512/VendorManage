from django.test import TestCase
from django.urls import reverse

from invoice.models import Invoice
from challan.models import Challan
from customer.models import Customer

class ChallanModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Customer.objects.create()
        Challan.objects.create(number=10, customer=Customer.objects.all()[0])

    def setUp(self):
        self.challan = Challan.objects.get(number=10)
        self.customer = Customer.objects.all()[0]
    
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

    def test_field_jobwork_gatepass_processed(self):
        field = self.challan._meta.get_field('jobwork_gatepass_processed')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)
        self.assertEqual(field.verbose_name, 'Jobwork GatePass (Processed)')
        self.assertEqual(field.upload_to(self.challan, 'test.jpg'), 'Challan/1/Images/test.jpg')

    def test_field_invoice(self):
        field = self.challan._meta.get_field('invoice')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)
        self.assertIsNone(field.default)

    def test_field_invoice_on_delete(self):
        field = self.challan._meta.get_field('invoice')
        invoice = Invoice.objects.create(number=10)
        invoice.add_challan(self.challan)
        self.assertEqual(invoice.challans.all().first(), self.challan)
        self.assertEqual(self.challan.invoice, invoice)
        Invoice.objects.all().delete()
        self.assertEqual(Challan.objects.all()[0].invoice, field.default)

    def test_field_customer(self):
        field = self.challan._meta.get_field('customer')
        self.assertTrue(field.null)
        self.assertFalse(field.blank)
        self.assertIsNone(field.default)

    def test_field_customer_on_delete(self):
        field = self.challan._meta.get_field('customer')
        customer = Customer.objects.create()
        self.challan.customer = customer
        self.challan.save()
        self.assertEqual(customer.challans.all().first(), self.challan)
        self.assertEqual(self.challan.customer, customer)
        Customer.objects.all().delete()
        self.assertEqual(Challan.objects.all()[0].customer, field.default)

    def test_method_get_all(self):
        self.assertQuerysetEqual(Challan.get_all(), Challan.objects.all(), transform=lambda x:x)

    def test_method_get_urls(self):
        self.assertEqual(Challan.get_list_url(), '/challan/')
        self.assertEqual(self.challan.get_absolute_url(), '/challan/10/view/')
        self.assertEqual(self.challan.get_printable_url(), '/challan/10/view/printable/')
        self.assertEqual(self.challan.get_update_url(), '/challan/1/update/')
        self.assertEqual(self.challan.get_delete_url(), '/challan/10/delete/')
        self.assertEqual(self.challan.get_excel_url(), '/challan/1/excel/')