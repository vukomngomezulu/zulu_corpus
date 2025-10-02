from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ZuluWord, UserSearchHistory, UserFavourite, WordPair
from .forms import SearchForm

def custom_logout(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    recent_words = ZuluWord.objects.order_by('-date_added')[:5]
    popular_words = ZuluWord.objects.annotate(
        search_count=Count('usersearchhistory')
    ).order_by('-search_count')[:5]
    
    return render(request, 'home.html', {
        'recent_words': recent_words,
        'popular_words': popular_words
    })

@login_required
def remove_history_entry(request, entry_id):
    """Remove one history entry"""
    try:
        entry = UserSearchHistory.objects.get(id=entry_id, user=request.user)
        entry.delete()
        messages.success(request, 'Search history entry removed.')
    except UserSearchHistory.DoesNotExist:
        messages.error(request, 'History entry not found.')
    
    return redirect('history')

@login_required
def clear_all_history(request):
    if request.method == 'POST':
        count, _ = UserSearchHistory.objects.filter(user=request.user).delete()
        messages.success(request, f'Cleared {count} history entries.')
    
    return redirect('history')

@login_required
def favourites(request):
    favourites = UserFavourite.objects.filter(
        user=request.user
    ).select_related('word').order_by('-date_added')
    
    return render(request, 'favourites.html', {'favourites': favourites})


@login_required
@csrf_exempt
def add_to_favourites(request, word_id):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error', 
            'message': 'Invalid request method. Only POST allowed.'
        }, status=405)
    
    try:
        word = get_object_or_404(ZuluWord, id=word_id)
        
        favourite, created = UserFavourite.objects.get_or_create(
            user=request.user,
            word=word
        )
        
        if not created:
            favourite.delete()
            return JsonResponse({
                'status': 'removed', 
                'message': 'Removed from favourites',
                'word_id': word_id,
                'word_name': word.zulu_word
            })
        else:
            return JsonResponse({
                'status': 'added', 
                'message': 'Added to favourites',
                'word_id': word_id,
                'word_name': word.zulu_word
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=500)


@login_required
def history(request):
    search_history = UserSearchHistory.objects.filter(
        user=request.user
    ).prefetch_related('search_results')[:5]
    
    return render(request, 'history.html', {'history': search_history})


@login_required
def trends(request):
    word_frequency = ZuluWord.objects.annotate(
        search_count=Count('usersearchhistory')
    ).order_by('-search_count')[:10]
    
    total_words = ZuluWord.objects.count()
    total_phrases = ZuluWord.objects.filter(
        Q(example_sentence_zulu__isnull=False) | Q(part_of_speech='phrase')
    ).count()
    total_users = User.objects.count()
    total_searches = UserSearchHistory.objects.count()
    
    return render(request, 'trends.html', {
        'word_frequency': word_frequency,
        'total_words': total_words,
        'total_phrases': total_phrases,
        'total_users': total_users,
        'total_searches': total_searches
    })


@login_required
def help_page(request):
    return render(request, 'help.html')


@login_required
def profile(request):
    user = request.user
    favourite_count = UserFavourite.objects.filter(user=user).count()
    search_count = UserSearchHistory.objects.filter(user=user).count()
    recent_searches = UserSearchHistory.objects.filter(
        user=user
    ).select_related('user').order_by('-search_date')[:5]
    
    return render(request, 'profile.html', {
        'user': user,
        'favourite_count': favourite_count,
        'search_count': search_count,
        'recent_searches': recent_searches
    })


def word_detail(request, word_id):
    word = get_object_or_404(ZuluWord, id=word_id)
    similar_words = ZuluWord.objects.filter(
        part_of_speech=word.part_of_speech
    ).exclude(id=word.id)[:5]
    
    return render(request, 'word_detail.html', {
        'word': word,
        'similar_words': similar_words
    })

def cultural_stories(request):
    return render(request,'cultural_stories.html')

@login_required
def search(request):
    form = SearchForm(request.GET or None)
    results = []
    query = request.GET.get('q', '').strip()
    
    if form.is_valid() and query:
        search_type = request.GET.get('search_type', 'word')
        part_of_speech = request.GET.get('pos', '')
        exact_match = request.GET.get('exact_match', False)
        
        search_conditions = _build_search_conditions(query, search_type, exact_match)
        
        if search_conditions:
            results = ZuluWord.objects.filter(search_conditions)
            
            if part_of_speech:
                results = results.filter(part_of_speech=part_of_speech)
            
            
            if results.exists():
                history = _save_search_history(request.user, query, results)
                
                
                _track_word_pairs(results)
    
    # Mark favourites for authenticated users
    if request.user.is_authenticated and results:
        _mark_favourites(request.user, results)
    
    return render(request, 'search.html', {
        'form': form,
        'results': results,
        'query': query,
    })

def _track_word_pairs(words):
    word_list = list(words)
    
    
    for i in range(len(word_list)):
        for j in range(i + 1, len(word_list)):
            WordPair.increment_pair_frequency(word_list[i], word_list[j])

def _build_search_conditions(query, search_type, exact_match):
    if not query or len(query) < 1:  #
        return None
    
    if len(query) >= 3:
        lookup = 'icontains'  
    else:
        lookup = 'iexact'  
    
    
    base_conditions = Q(
        **{f'zulu_word__{lookup}': query}) | Q(
        **{f'english_translation__{lookup}': query}) | Q(
        **{f'swati_translation__{lookup}': query}) | Q(
        **{f'sotho_translation__{lookup}': query}
    )
    
    if search_type == 'phrase':
        base_conditions |= Q(
            **{f'example_sentence_zulu__{lookup}': query}) | Q(
            **{f'example_sentence_english__{lookup}': query}) | Q(
            **{f'example_sentence_swati__{lookup}': query}) | Q(
            **{f'example_sentence_sotho__{lookup}': query}
        )
    elif search_type == 'definition':
        base_conditions |= Q(**{f'cultural_context__{lookup}': query})
    
    return base_conditions

def _save_search_history(user, query, results):
    #SAVING ONLY IF WE HAV RESULYSs
    if results.exists():  
        history = UserSearchHistory.objects.create(user=user, search_query=query)
        history.search_results.set(results[:10])  # Limit to first 10 results

def _mark_favourites(user, words):
    favourite_word_ids = UserFavourite.objects.filter(
        user=user, word__in=words
    ).values_list('word_id', flat=True)
    
    for word in words:
        word.is_favourite = word.id in favourite_word_ids