# main_app/utils/json_loader.py
import json
import os
from django.conf import settings
from main_app.models import ZuluWord, WordPair

def load_words_from_json():
    """Load words from JSON file into database"""
    json_file_path = os.path.join(settings.BASE_DIR, 'data.json')
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # ZuluWord.objects.all().delete()
        # WordPair.objects.all().delete()
        
        # Load words
        words_created = 0
        words_updated = 0
        
        for word_data in data['words']:
            # Handle empty fields by providing defaults
            defaults = {
                'english_translation': word_data.get('english_translation', ''),
                'swati_translation': word_data.get('swati_translation', ''),
                'sotho_translation': word_data.get('sotho_translation', ''),
                'pronunciation_guide': word_data.get('pronunciation_guide', ''),
                'part_of_speech': word_data.get('part_of_speech', 'noun'),
                'cultural_context': word_data.get('cultural_context', ''),
                'example_sentence_zulu': word_data.get('example_sentence_zulu', ''),
                'example_sentence_english': word_data.get('example_sentence_english', ''),
                'example_sentence_swati': word_data.get('example_sentence_swati', ''),
                'example_sentence_sotho': word_data.get('example_sentence_sotho', ''),
            }
            
            word, created = ZuluWord.objects.update_or_create(
                zulu_word=word_data['zulu_word'],
                defaults=defaults
            )
            
            if created:
                words_created += 1
            else:
                words_updated += 1
        
        # Load word pairs
        pairs_created = 0
        for pair_data in data.get('word_pairs', []):
            try:
                word1 = ZuluWord.objects.get(zulu_word=pair_data['word1_zulu'])
                word2 = ZuluWord.objects.get(zulu_word=pair_data['word2_zulu'])
                
                pair, created = WordPair.objects.get_or_create(
                    word1=word1,
                    word2=word2,
                    defaults={'frequency': pair_data.get('frequency', 1)}
                )
                
                if created:
                    pairs_created += 1
                    
            except ZuluWord.DoesNotExist:
                print(f"Warning: Could not find words for pair: {pair_data}")
                continue
        
        return {
            'words_created': words_created,
            'words_updated': words_updated,
            'pairs_created': pairs_created
        }
        
    except FileNotFoundError:
        print("JSON file not found at:", json_file_path)
        return {'error': 'File not found'}
    except json.JSONDecodeError as e:
        print("Invalid JSON format:", e)
        return {'error': 'Invalid JSON'}
    except Exception as e:
        print("Error loading JSON data:", e)
        return {'error': str(e)}