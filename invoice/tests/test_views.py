from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission, User
from django.conf import settings

from invoice.models import Invoice
from challan.models import Challan
from customer.models import Customer

# class InvoiceUpdateViewTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         Invoice.objects.create(number=10)
#         Customer.objects.create(name='customer1')
#         Customer.objects.create(name='customer2')
#         for i in range(10):
#             Challan.objects.create(number=i+1, customer=Customer.objects.get(id=1))
#         for i in range(10):
#             Challan.objects.create(number=i+11, customer=Customer.objects.get(id=2))
#         test_user1 = User.objects.create_user(username='user1', password='2020')
#         test_user2 = User.objects.create_user(username='user2', password='2020')
#         perm = Permission.objects.get(codename='view_invoice', content_type__app_label='invoice')
#         test_user2.user_permissions.add(perm)
#         perm = Permission.objects.get(codename='view_challan', content_type__app_label='challan')
#         test_user2.user_permissions.add(perm)
#         test_user1.save()
#         test_user2.save()

#     def setUp(self):
#         self.invoice = Invoice.objects.get(number=10)
#         self.url = reverse('invoice:printable', kwargs={'slug': 10})

#     def test_view_redirect_if_not_logged_in(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse(settings.LOGIN_URL)+'?next=/invoice/10/view/printable/')

#     def test_view_url_exists_at_location(self):
#         response = self.client.get('/invoice/10/view/printable/')
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse(settings.LOGIN_URL)+'?next=/invoice/10/view/printable/')

#     def test_view_url_permission_denied(self):
#         login = self.client.login(username='user1', password='2020')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)

#     def test_view_url_correct_permission(self):
#         login = self.client.login(username='user2', password='2020')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)

#     def test_view_uses_correct_template(self):
#         login = self.client.login(username='user2', password='2020')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'invoice/invoice_detail_printable.html')

#     def test_view_invoice_present_in_context(self):
#         login = self.client.login(username='user2', password='2020')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context['invoice'], self.invoice)

#     def test_view_challan_list_present_in_context(self):
#         login = self.client.login(username='user2', password='2020')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('challan_list', response.context)

#     def test_view_challan_list_content(self):
#         self.invoice.add_challan(Challan.objects.get(number=1))
#         self.invoice.add_challan(Challan.objects.get(number=10))
#         login = self.client.login(username='user2', password='2020')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context['challan_list'].count(), 2)
#         cl = response.context['challan_list'].values_list('number', flat=True)
#         cl = list(cl)
#         self.assertEqual(cl, [1,10])

class InvoicePrintableView(TestCase):
    @classmethod
    def setUpTestData(cls):
        Invoice.objects.create(number=10)
        Customer.objects.create(name='customer1')
        Customer.objects.create(name='customer2')
        for i in range(10):
            Challan.objects.create(number=i+1, customer=Customer.objects.get(id=1))
        for i in range(10):
            Challan.objects.create(number=i+11, customer=Customer.objects.get(id=2))
        test_user1 = User.objects.create_user(username='user1', password='2020')
        test_user2 = User.objects.create_user(username='user2', password='2020')
        perm = Permission.objects.get(codename='view_invoice', content_type__app_label='invoice')
        test_user2.user_permissions.add(perm)
        perm = Permission.objects.get(codename='view_challan', content_type__app_label='challan')
        test_user2.user_permissions.add(perm)
        test_user1.save()
        test_user2.save()

    def setUp(self):
        self.invoice = Invoice.objects.get(number=10)
        self.url = reverse('invoice:printable', kwargs={'slug': 10})

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_URL)+'?next=/invoice/10/view/printable/')

    def test_view_url_exists_at_location(self):
        response = self.client.get('/invoice/10/view/printable/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_URL)+'?next=/invoice/10/view/printable/')

    def test_view_url_permission_denied(self):
        login = self.client.login(username='user1', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_view_url_correct_permission(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice/invoice_detail_printable.html')

    def test_view_invoice_present_in_context(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['invoice'], self.invoice)

    def test_view_challan_list_present_in_context(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('challan_list', response.context)

    def test_view_challan_list_content(self):
        self.invoice.add_challan(Challan.objects.get(number=1))
        self.invoice.add_challan(Challan.objects.get(number=10))
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['challan_list'].count(), 2)
        cl = response.context['challan_list'].values_list('number', flat=True)
        cl = list(cl)
        self.assertEqual(cl, [1,10])

class InvoiceDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Invoice.objects.create(number=10)
        Customer.objects.create(name='customer1')
        Customer.objects.create(name='customer2')
        for i in range(10):
            Challan.objects.create(number=i+1, customer=Customer.objects.get(id=1))
        for i in range(10):
            Challan.objects.create(number=i+11, customer=Customer.objects.get(id=2))
        test_user1 = User.objects.create_user(username='user1', password='2020')
        test_user2 = User.objects.create_user(username='user2', password='2020')
        perm = Permission.objects.get(codename='view_invoice', content_type__app_label='invoice')
        test_user2.user_permissions.add(perm)
        perm = Permission.objects.get(codename='view_challan', content_type__app_label='challan')
        test_user2.user_permissions.add(perm)
        test_user1.save()
        test_user2.save()

    def setUp(self):
        self.invoice = Invoice.objects.get(number=10)
        self.url = reverse('invoice:detail', kwargs={'slug': 10})

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_URL)+'?next=/invoice/10/view/')

    def test_view_url_exists_at_location(self):
        response = self.client.get('/invoice/10/view/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_URL)+'?next=/invoice/10/view/')

    def test_view_url_permission_denied(self):
        login = self.client.login(username='user1', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_view_url_correct_permission(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_navigation_value(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('invoice', response.context_data['view'].navigation)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice/invoice_detail.html')

    def test_view_invoice_present_in_context(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['invoice'], self.invoice)

    def test_view_challan_list_present_in_context(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('challan_list', response.context)

    def test_view_context_challan_list_without_customers(self):
        """tests that the challan list consists of all the challans
        if the invoice doesnt already have a challan"""
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['challan_list'].count(), 20)

    def test_view_challan_list2(self):
        """tests that the challan list consists of all the remaining
        challans of the same customer as the invoice"""
        self.invoice.add_challan(Challan.objects.get(number=1))
        self.invoice.add_challan(Challan.objects.get(number=10))
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['challan_list'].count(), 8)
        cl = response.context['challan_list'].values_list('number', flat=True)
        cl = list(cl)
        self.assertEqual(cl, list(range(9,1,-1)))


class InvoiceListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_invoices = 25
        for i in range(number_of_invoices):
            Invoice.objects.create(number=i+1)
        test_user1 = User.objects.create_user(username='user1', password='2020')
        test_user2 = User.objects.create_user(username='user2', password='2020')
        perm = Permission.objects.get(codename='view_invoice', content_type__app_label='invoice')
        test_user2.user_permissions.add(perm)
        test_user1.save()
        test_user2.save()

    def setUp(self):
        pass

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('invoice:list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/invoice/')

    def test_view_url_exists_at_location(self):
        response = self.client.get('/invoice/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/invoice/')

    def test_view_url_permission_denied(self):
        login = self.client.login(username='user1', password='2020')
        response = self.client.get(reverse('invoice:list'))
        self.assertEqual(response.status_code, 403)

    def test_view_url_correct_permission(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(reverse('invoice:list'))
        self.assertEqual(response.status_code, 200)

    def test_view_navigation_value(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(reverse('invoice:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual('invoice', response.context_data['view'].navigation)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(reverse('invoice:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice/invoice_list.html')

    def test_view_invoice_list_in_context(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(reverse('invoice:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('invoice_list', response.context)
        self.assertEqual(response.context['invoice_list'].count(), 25)

    def test_view_ordering(self):
        login = self.client.login(username='user2', password='2020')
        response = self.client.get(reverse('invoice:list'))
        self.assertEqual(response.status_code, 200)
        il = response.context['invoice_list'].values_list('number', flat=True)
        il = list(il)
        self.assertEqual(il, list(range(25,0,-1)))