
import time
from django.test import TestCase
from django.contrib.auth.models import User
from main_app.models import ZuluWord

class PageLoadPerformanceTests(TestCase):
    def setUp(self):
        """Create a test user and log in"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_home_page_load_time(self):
        """Test home page loads within acceptable time"""
        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()
        
        load_time = end_time - start_time
        
        # Handle both 200 (direct access) and 302 (redirect) cases
        if response.status_code == 302:
            # Follow the redirect and test that page
            redirect_response = self.client.get(response.url)
            self.assertEqual(redirect_response.status_code, 200)
            print(f"Home page redirected to {response.url} and loaded in {load_time:.3f} seconds")
        else:
            self.assertEqual(response.status_code, 200)
            print(f"Home page loaded directly in {load_time:.3f} seconds")
        
        self.assertLess(load_time, 2.0)
    
    def test_search_results_load_time(self):
        """Test search results page performance"""
        # Create test data
        ZuluWord.objects.create(
            zulu_word="sawubona",
            english_translation="hello",
            part_of_speech="greeting"
        )
        
        start_time = time.time()
        response = self.client.get('/search/', {'q': 'sawubona'})
        end_time = time.time()
        
        load_time = end_time - start_time
        
        # Handle redirects for search page too
        if response.status_code == 302:
            redirect_response = self.client.get(response.url)
            self.assertEqual(redirect_response.status_code, 200)
        else:
            self.assertEqual(response.status_code, 200)
        
        self.assertLess(load_time, 1.5)
        print(f"Search results loaded in {load_time:.3f} seconds")
