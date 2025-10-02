from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ZuluWord(models.Model):
    PARTS_OF_SPEECH = [
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('greeting', 'Greeting'),
        ('farewell', 'Farewell'),
        ('phrase', 'Phrase'),
    ]
    
    zulu_word = models.CharField(max_length=100)
    english_translation = models.CharField(max_length=100)
    swati_translation = models.CharField(max_length=100)
    sotho_translation = models.CharField(max_length=100)
    pronunciation_guide = models.CharField(max_length=100, blank=True)
    part_of_speech = models.CharField(max_length=50, choices=PARTS_OF_SPEECH)
    cultural_context = models.TextField(blank=True)
    example_sentence_zulu = models.TextField(blank=True)
    example_sentence_english = models.TextField(blank=True)
    example_sentence_swati = models.TextField(blank=True)
    example_sentence_sotho = models.TextField(blank=True)
    synonyms = models.ManyToManyField('self', blank=True, symmetrical=False)
    date_added = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.zulu_word

class WordPair(models.Model):
    word1 = models.ForeignKey(ZuluWord, on_delete=models.CASCADE, related_name='word1_pair')
    word2 = models.ForeignKey(ZuluWord, on_delete=models.CASCADE, related_name='word2_pair')
    frequency = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ('word1', 'word2')
    
    def __str__(self):
        return f"{self.word1.zulu_word} - {self.word2.zulu_word}"
    
    @classmethod
    def increment_pair_frequency(cls, word1, word2):
        # Ensure consistent ordering to avoid duplicate pairs
        if word1.id > word2.id:
            word1, word2 = word2, word1
            
        pair, created = cls.objects.get_or_create(
            word1=word1,
            word2=word2,
            defaults={'frequency': 1}
        )
        
        if not created:
            pair.frequency += 1
            pair.save()

class UserSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_query = models.CharField(max_length=255)
    search_results = models.ManyToManyField(ZuluWord)
    search_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.search_query}"
    
    def delete_history_entry(self):
        self.delete()

class UserFavourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(ZuluWord, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'word')
    
    def __str__(self):
        return f"{self.user.username} - {self.word.zulu_word}"