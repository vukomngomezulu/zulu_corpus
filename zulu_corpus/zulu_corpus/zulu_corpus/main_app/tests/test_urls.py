from django.test import TestCase
from django.urls import reverse, resolve
from main_app import views

class URLTests(TestCase):
    def test_home_url_resolves(self):
        """Test that home URL resolves to correct view"""
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.home)
    
    def test_search_url_resolves(self):
        """Test that search URL resolves to correct view"""
        url = reverse('search')
        self.assertEqual(resolve(url).func, views.search)