from django.test import TestCase, Client, LiveServerTestCase 
from django.urls import reverse 
from django.contrib.auth.models import User 
from main_app.models import ZuluWord, UserFavourite, UserSearchHistory 
import time 
 
class EndToEndWorkflowTests(LiveServerTestCase): 
    def setUp(self): 
        self.client = Client() 
        self.user = User.objects.create_user(username="systemuser", password="systempass123") 
        self.words = [ 
            ZuluWord.objects.create(zulu_word="sawubona", english_translation="hello", swati_translation="sawubona", sotho_translation="dumela", part_of_speech="greeting"), 
            ZuluWord.objects.create(zulu_word="amanzi", english_translation="water", swati_translation="emanti", sotho_translation="metsi", part_of_speech="noun") 
        ] 
 
    def test_complete_user_journey(self): 
        print("Testing: Complete User Journey") 
        self.client.login(username="systemuser", password="systempass123") 
        response = self.client.get(reverse('home')) 
        self.assertEqual(response.status_code, 200) 
        print("Complete user journey test passed!") 
 
class DataValidationSystemTests(TestCase): 
    def setUp(self): 
        self.user = User.objects.create_user(username="datauser", password="datapass123") 
        self.client = Client() 
        self.client.login(username="datauser", password="datapass123") 
 
    def test_data_integrity_across_operations(self): 
        print("Testing: Data Integrity") 
        word1 = ZuluWord.objects.create(zulu_word="uthando", english_translation="love", swati_translation="lutsandvo", sotho_translation="lerato", part_of_speech="noun") 
        initial_word_count = ZuluWord.objects.count() 
        response = self.client.get(reverse('search'), {'q': 'love'}) 
        self.assertEqual(response.status_code, 200) 
        response = self.client.post(reverse('add_to_favourites', args=[word1.id])) 
        self.assertEqual(response.status_code, 200) 
        final_word_count = ZuluWord.objects.count() 
        self.assertEqual(initial_word_count, final_word_count) 
        favourites_count = UserFavourite.objects.count() 
        self.assertEqual(favourites_count, 1) 
        print("Data integrity test passed!") 
 
class ErrorHandlingSystemTests(TestCase): 
    def setUp(self): 
        self.user = User.objects.create_user(username="erroruser", password="errorpass123") 
        self.client = Client() 
        self.client.login(username="erroruser", password="errorpass123") 
 
    def test_error_handling_system(self): 
        print("Testing: Error Handling System") 
        response = self.client.get(reverse('search'), {'q': ''}) 
        self.assertEqual(response.status_code, 200) 
        long_query = "a" * 100 
        response = self.client.get(reverse('search'), {'q': long_query}) 
        self.assertEqual(response.status_code, 200) 
        response = self.client.get(reverse('word_detail', args=[9999])) 
        self.assertEqual(response.status_code, 404) 
        print("Error handling test passed!") 
 
class MultiUserSystemTests(TestCase): 
    def test_multi_user_data_isolation(self): 
        print("Testing: Multi-User Data Isolation") 
        user1 = User.objects.create_user(username="user1", password="pass1") 
        user2 = User.objects.create_user(username="user2", password="pass2") 
        client1 = Client() 
        client2 = Client() 
        word = ZuluWord.objects.create(zulu_word="ubuntu", english_translation="humanity", swati_translation="buntfu", sotho_translation="botho", part_of_speech="noun") 
        client1.login(username="user1", password="pass1") 
        response = client1.post(reverse('add_to_favourites', args=[word.id])) 
        self.assertEqual(response.status_code, 200) 
        client2.login(username="user2", password="pass2") 
        response = client2.post(reverse('add_to_favourites', args=[word.id])) 
        self.assertEqual(response.status_code, 200) 
        user1_favourites = UserFavourite.objects.filter(user=user1).count() 
        user2_favourites = UserFavourite.objects.filter(user=user2).count() 
        self.assertEqual(user1_favourites, 1) 
        self.assertEqual(user2_favourites, 1) 
        print("Multi-user test passed!") 
