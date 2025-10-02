from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from main_app.models import ZuluWord

class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", 
            password="testpass123"
        )
    
    def test_home_view_requires_login(self):
        """Test that home view redirects to login if not authenticated"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_home_view_authenticated(self):
        """Test home view when user is authenticated"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

class SearchViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", 
            password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        
        # Create test word
        self.word = ZuluWord.objects.create(
            zulu_word="ithuba",
            english_translation="time",
            swati_translation="likhefu",
            sotho_translation="nako", 
            part_of_speech="noun"
        )
    
    def test_search_functionality(self):
        """Test basic search functionality"""
        response = self.client.get(reverse('search'), {'q': 'time'})
        self.assertEqual(response.status_code, 200)