from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
import unittest.mock as mock
import io
import json
import os

from .models import Product, AuditLog
from .forms import productForm


class InventoryTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='password123')
        self.p1 = Product.objects.create(
            name='Blue Jeans', sku='JEA-1001', price=40.0, quantity=10, supplier='DenimCo'
        )
        self.p2 = Product.objects.create(
            name='Running Shoes', sku='SHO-2002', price=80.0, quantity=0, supplier='Bata'
        )
        self.p3 = Product.objects.create(
            name='Leather Jacket', sku='JAC-3003', price=150.0, quantity=5, supplier='LeatherCo'
        )

    # 1. Search, filter and sort
    def test_search_by_name_and_sku(self):
        self.client.login(username='tester', password='password123')
        # Search by name
        res = self.client.get(reverse('product_list'), {'q': 'Shoes'})
        self.assertContains(res, 'Running Shoes')
        self.assertNotContains(res, 'Blue Jeans')

        # Search by SKU
        res = self.client.get(reverse('product_list'), {'q': 'JEA-1001'})
        self.assertContains(res, 'Blue Jeans')
        self.assertNotContains(res, 'Running Shoes')

    def test_filter_and_sort_together(self):
        self.client.login(username='tester', password='password123')
        # Filter stock: in_stock, sorted by price descending
        res = self.client.get(reverse('product_list'), {'stock': 'in_stock', 'sort': 'price_desc'})
        self.assertEqual(res.status_code, 200)
        products = list(res.context['page_obj'])
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].name, 'Leather Jacket') # $150
        self.assertEqual(products[1].name, 'Blue Jeans')      # $40

    # 2. Pagination
    def test_pagination(self):
        self.client.login(username='tester', password='password123')
        # Add additional products to test pagination (page size = 5)
        for i in range(4, 9):
            Product.objects.create(
                name=f'Product {i}', sku=f'PRD-{i:04d}', price=10.0 + i, quantity=i, supplier='Supplier'
            )
        res = self.client.get(reverse('product_list'), {'page': 1})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['page_obj']), 5)
        self.assertTrue(res.context['page_obj'].has_next())

        res_p2 = self.client.get(reverse('product_list'), {'page': 2})
        self.assertEqual(res_p2.status_code, 200)
        self.assertEqual(len(res_p2.context['page_obj']), 3)

    # 3. Auth
    def test_auth_protection(self):
        # Unauthenticated redirects to login
        res_list = self.client.get(reverse('product_list'))
        self.assertEqual(res_list.status_code, 302)
        self.assertIn('/login/', res_list.url)

        res_create = self.client.get(reverse('product_create'))
        self.assertEqual(res_create.status_code, 302)

        res_bot = self.client.get(reverse('chatbot'))
        self.assertEqual(res_bot.status_code, 302)

        # Authenticated succeeds
        self.client.login(username='tester', password='password123')
        res_list_auth = self.client.get(reverse('product_list'))
        self.assertEqual(res_list_auth.status_code, 200)

        # Logout redirects to login
        res_logout = self.client.get(reverse('logout'))
        self.assertEqual(res_logout.status_code, 302)
        self.assertEqual(res_logout.url, reverse('login'))

    # 4. Strict SKU validation
    def test_sku_validation(self):
        # Model full_clean validation
        invalid_p = Product(name='Bad', sku='invalid_sku', price=10, quantity=1, supplier='Test')
        with self.assertRaises(ValidationError):
            invalid_p.full_clean()

        # Form validation
        form_bad = productForm(data={'name': 'Bad', 'sku': '123-ABCD', 'price': 10, 'quantity': 1, 'supplier': 'Test'})
        self.assertFalse(form_bad.is_valid())
        self.assertIn('sku', form_bad.errors)

        form_lowercase = productForm(data={'name': 'Good', 'sku': 'abc-5678', 'price': 10, 'quantity': 1, 'supplier': 'Test'})
        self.assertTrue(form_lowercase.is_valid())
        self.assertEqual(form_lowercase.cleaned_data['sku'], 'ABC-5678')

    # 5. Audit trail
    def test_audit_trail_crud_and_snapshot(self):
        self.client.login(username='tester', password='password123')
        # Create
        res = self.client.post(reverse('product_create'), {
            'name': 'Audit Hat', 'sku': 'HAT-9999', 'price': 25.0, 'quantity': 7, 'supplier': 'HatCo'
        })
        hat = Product.objects.get(sku='HAT-9999')
        c_log = AuditLog.objects.filter(product_id=hat.product_id, action=AuditLog.ACTION_CREATE).first()
        self.assertIsNotNone(c_log)
        self.assertEqual(c_log.username, 'tester')
        self.assertEqual(c_log.product_snapshot['sku'], 'HAT-9999')

        # Update
        self.client.post(reverse('product_update', args=[hat.product_id]), {
            'name': 'Audit Hat', 'sku': 'HAT-9999', 'price': 30.0, 'quantity': 12, 'supplier': 'HatCo'
        })
        u_log = AuditLog.objects.filter(product_id=hat.product_id, action=AuditLog.ACTION_UPDATE).first()
        self.assertIsNotNone(u_log)
        self.assertEqual(u_log.changes['price'], {'old': 25.0, 'new': 30.0})
        self.assertEqual(u_log.changes['quantity'], {'old': 7, 'new': 12})

        # Delete
        pid = hat.product_id
        self.client.post(reverse('product_delete', args=[pid]))
        d_log = AuditLog.objects.filter(product_id=pid, action=AuditLog.ACTION_DELETE).first()
        self.assertIsNotNone(d_log)
        self.assertEqual(d_log.product_snapshot['name'], 'Audit Hat')
        self.assertEqual(d_log.product_snapshot['sku'], 'HAT-9999')

        # Read-only history page renders
        res_hist = self.client.get(reverse('audit_history'))
        self.assertEqual(res_hist.status_code, 200)
        self.assertContains(res_hist, 'HAT-9999')

    # 6. AI Chatbot
    def test_chatbot_without_api_key(self):
        self.client.login(username='tester', password='password123')
        if 'GROQ_API_KEY' in os.environ:
            del os.environ['GROQ_API_KEY']
        res = self.client.post(reverse('chatbot'), {'message': 'How many jeans do we have?'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Groq API key not configured')

    def test_chatbot_mocked_interaction_and_clear(self):
        self.client.login(username='tester', password='password123')
        os.environ['GROQ_API_KEY'] = 'fake_key'

        mock_resp = io.BytesIO(json.dumps({
            'choices': [{'message': {'content': 'You have 10 Blue Jeans in stock.'}}]
        }).encode('utf-8'))

        with mock.patch('urllib.request.urlopen', return_value=mock_resp):
            res = self.client.post(reverse('chatbot'), {'message': 'Blue jeans stock?'}, follow=True)
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, 'You have 10 Blue Jeans in stock.')

        # Clear history
        res_clear = self.client.get(reverse('chatbot_clear'), follow=True)
        self.assertEqual(res_clear.status_code, 200)
        self.assertEqual(len(self.client.session.get('chat_history', [])), 0)

        del os.environ['GROQ_API_KEY']
