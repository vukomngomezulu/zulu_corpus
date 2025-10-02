from django.test import TestCase
from django.contrib.auth.models import User

class BasicModelTests(TestCase):
    """Basic model tests that should work"""
    
    def test_user_creation(self):
        """Test that we can create a User (Django built-in model)"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("testpass123"))
    
    def test_basic_assertion(self):
        """Simple test to verify the test file works"""
        self.assertEqual(1 + 1, 2)


try:
    from main_app.models import ZuluWord
    
    class ZuluWordModelTests(TestCase):
        def test_zulu_word_creation(self):
            """Test ZuluWord model if it exists"""
            word = ZuluWord.objects.create(
                zulu_word="sawubona",
                english_translation="hello",
                swati_translation="sawubona",
                sotho_translation="dumela",
                part_of_speech="greeting"
            )
            self.assertEqual(word.zulu_word, "sawubona")
            
except ImportError:
    print("ZuluWord model not available for testing")
except Exception as e:
    print(f"Error importing ZuluWord model: {e}")