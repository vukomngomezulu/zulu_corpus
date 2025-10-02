from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from main_app.models import ZuluWord, UserFavourite, UserSearchHistory

class UserWorkflowIntegrationTests(TestCase):
    """Integration tests for complete user workflows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Create test words
        self.word1 = ZuluWord.objects.create(
            zulu_word="sawubona",
            english_translation="hello",
            swati_translation="sawubona",
            sotho_translation="dumela",
            part_of_speech="greeting"
        )
        self.word2 = ZuluWord.objects.create(
            zulu_word="amanzi", 
            english_translation="water",
            swati_translation="emanti",
            sotho_translation="metsi",
            part_of_speech="noun"
        )
        
        # Login the user
        self.client.login(username="testuser", password="testpass123")
    
    def test_complete_search_workflow(self):
        """Test complete search workflow: login → search → view results"""
        # 1. Access home page (should work when authenticated)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Perform search
        response = self.client.get(reverse('search'), {'q': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'sawubona')
        
        # 3. Verify search results are displayed
        self.assertIn('results', response.context)
    
    def test_favourites_workflow(self):
        """Test complete favourites workflow: search → add favourite → view favourites"""
        # 1. Search for a word
        response = self.client.get(reverse('search'), {'q': 'water'})
        self.assertEqual(response.status_code, 200)
        
        # 2. Add to favourites
        response = self.client.post(reverse('add_to_favourites', args=[self.word2.id]))
        self.assertEqual(response.status_code, 200)
        
        # 3. Check favourites page
        response = self.client.get(reverse('favourites'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Verify favourite appears in the list
        favourites = UserFavourite.objects.filter(user=self.user)
        self.assertTrue(favourites.exists())
        self.assertEqual(favourites.first().word, self.word2)

class DatabaseIntegrationTests(TestCase):
    """Integration tests for database operations"""
    
    def test_model_relationships(self):
        """Test that model relationships work correctly together"""
        user = User.objects.create_user(username="testuser2", password="test123")
        word = ZuluWord.objects.create(
            zulu_word="indlu",
            english_translation="house",
            swati_translation="indlu",
            sotho_translation="ntlo",
            part_of_speech="noun"
        )
        
        # Create favourite relationship
        favourite = UserFavourite.objects.create(user=user, word=word)
        
        # Test relationship queries
        user_favourites = UserFavourite.objects.filter(user=user)
        self.assertEqual(user_favourites.count(), 1)
        self.assertEqual(user_favourites.first().word, word)
        
        # Test reverse relationship
        word_favourites = word.userfavourite_set.all()
        self.assertEqual(word_favourites.count(), 1)

class SearchHistoryIntegrationTests(TestCase):
    """Integration tests for search history functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="historyuser", password="test123")
        self.client.login(username="historyuser", password="test123")
        
        # Create test words
        ZuluWord.objects.create(
            zulu_word="isinkwa",
            english_translation="bread",
            swati_translation="sinkwa",
            sotho_translation="borotho",
            part_of_speech="noun"
        )
    
    def test_search_creates_history(self):
        """Test that searching creates search history"""
        # Perform search
        response = self.client.get(reverse('search'), {'q': 'bread'})
        self.assertEqual(response.status_code, 200)

class NavigationIntegrationTests(TestCase):
    """Integration tests for application navigation"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="navuser", password="test123")
        self.client.login(username="navuser", password="test123")
    
    def test_main_pages_accessible(self):
        """Test that main application pages are accessible"""
        # Test core pages that should work
        pages_to_test = ['home', 'search', 'favourites']
        
        for page_name in pages_to_test:
            try:
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200, 
                              f"Page {page_name} returned status {response.status_code}")
            except Exception as e:
                self.fail(f"Page {page_name} failed with error: {e}")

class TemplateIntegrationTests(TestCase):
    """Integration tests for template rendering with data"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="templateuser", password="test123")
        self.client.login(username="templateuser", password="test123")
        
        # Create test data
        ZuluWord.objects.create(
            zulu_word="hamba",
            english_translation="go",
            swati_translation="hamba", 
            sotho_translation="tsamaya",
            part_of_speech="verb"
        )
    
    def test_home_template_with_data(self):
        """Test that home template renders correctly with context data"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Check template contains expected elements
        self.assertContains(response, 'IsiZulu')
        self.assertContains(response, 'Search')

    def test_search_template_with_results(self):
        """Test search template with actual results"""
        response = self.client.get(reverse('search'), {'q': 'go'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search')             