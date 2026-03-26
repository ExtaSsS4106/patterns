from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from django.http import HttpResponse, JsonResponse
from .forms import *
from .models import *
from django.db import models
import json
import logging
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
"""Рендер первой страницы"""
def index(request):
    categories = Categories.objects.all()
    patterns = Patterns.objects.all()
    return render(request, 'test/index.html', {"categories": categories, "patterns":patterns})
"""Рендер определённого каталога по названию"""
def catalog(request, title):
    category = get_object_or_404(Categories, title=title)
    if category.title == title:
        patterns = Patterns.objects.filter(categories=category)
        data = []
        for pattern in patterns:
            raitng = Ratings.objects.get(patterns=pattern)
            data.append(
                {
                    "pattern": pattern,
                    "raitng": raitng
                }
            )
        return render(request, 'test/catalog.html', {"patterns": data})
    return render(request, 'test/catalog.html', {"patterns": "None"})
"""Рендер страницы одного из патернов по id"""
def pattern_detail(request, id):
    pattern = get_object_or_404(Patterns, id=id)
    raitng = Ratings.objects.get(patterns=pattern)
    data = {
            "pattern": pattern,
            "raitng": raitng
        }
    return render(request, 'test/pattern-detail.html', data)

@login_required
def check_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    pattern_id = data.get('pattern_id')
    profile = Profiles.objects.get(user=request.user)
    
    is_favorite = Favorites.objects.filter(
        users=profile,
        patterns_id=pattern_id
    ).exists()
    
    return JsonResponse({'is_favorite': is_favorite})


def get_ratings(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    pattern_id = data.get('pattern_id')
    
    rating = Ratings.objects.filter(patterns_id=pattern_id).first()
    
    return JsonResponse({
        'likes': rating.likes if rating and rating.likes else 0,
        'dislikes': rating.dislikes if rating and rating.dislikes else 0
    })

"""
    Поставить дизлайк (убрать из избранного)
    Убрать дизлайк
"""
@login_required
def set_dislike(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    profile = Profiles.objects.get(user=request.user)
    data = json.loads(request.body)
    pattern_id = data.get('pattern_id')
    pattern = get_object_or_404(Patterns, id=pattern_id)
    rating = get_object_or_404(Ratings, patterns__id=pattern_id)
    fav = Favorites.objects.filter(users=profile, patterns=pattern).order_by('-id')
    rat_prof, created = Rating_profiles.objects.get_or_create(profiles=profile, ratings=rating)
    if rat_prof.dislike:

        if rating.dislikes is not None and rating.dislikes > 0:
            rating.dislikes -= 1
            rating.save()
            rat_prof.dislike = False
            rat_prof.save()
        return JsonResponse({'status': 'ok'}, status=200)
    elif rat_prof.like:
        if fav.exists():
            fav.delete()
        if rating.dislikes is None:
            rating.dislikes = 1
        else:
            rating.dislikes += 1
        rating.save()
        rat_prof.dislike = True
        rat_prof.save()
        return JsonResponse({'status': 'ok'}, status=200)
    else:
        if fav.exists():
            fav.delete()
        if rating.dislikes is None:
            rating.dislikes = 1
        else:
            rating.dislikes += 1
        rating.save()
        rat_prof.dislike = True
        rat_prof.save()
        return JsonResponse({'status': 'ok'}, status=200)

"""
    Добавить в избранное (добавить лайк)
    Убрать лайк (убрать из избранного)    
"""
@login_required
def set_like(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    profile = Profiles.objects.get(user=request.user)
    data = json.loads(request.body)
    pattern_id = data.get('pattern_id')
    pattern = get_object_or_404(Patterns, id=pattern_id)
    rating = get_object_or_404(Ratings, patterns__id=pattern_id)
    fav = Favorites.objects.filter(users=profile, patterns=pattern).order_by('-id')
    rat_prof, created = Rating_profiles.objects.get_or_create(profiles=profile, ratings=rating)
    if rat_prof.like:
        if fav.exists():
            fav.delete()
        if rating.likes is not None and rating.likes > 0:
            rating.likes -= 1
            rating.save()
            rat_prof.like = False
            rat_prof.save()
        return JsonResponse({'status': 'ok'}, status=200)
    elif rat_prof.dislike:
        fav.create(
            users=profile,
            patterns=pattern
        )
        if rating.likes is None:
            rating.likes = 1
        else:
            rating.likes += 1
        rating.save()
        rat_prof.like = True
        rat_prof.save()
        return JsonResponse({'status': 'ok'}, status=200)
    else:
        fav.create(
            users=profile,
            patterns=pattern
        )
        if rating.likes is None:
            rating.likes = 1
        else:
            rating.likes += 1
        rating.save()
        rat_prof.like = True
        rat_prof.save()
        return JsonResponse({'status': 'ok'}, status=200)


"""API для добавления комментария"""
@login_required
def add_comment(request):
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        pattern_id = data.get('pattern_id')
        text = data.get('text', '').strip()
        if not text:
            return JsonResponse({'error': 'Текст комментария не может быть пустым'}, status=400)
        
        pattern = get_object_or_404(Patterns, id=pattern_id)
        profile = Profiles.objects.get(user=request.user)
        comment = Comments.objects.create(
            patterns=pattern,
            users=profile,
            comment=text
        )
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'text': comment.comment,
                'created_at': comment.created_at,
                'user_name': profile.user.username
            }
        })
        
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)

"""API для вывода комментариев"""
@csrf_exempt
def select_comments(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        pattern_id = data.get('pattern_id')
        pattern = get_object_or_404(Patterns, id=pattern_id)
        
        comments = Comments.objects.filter(patterns=pattern).select_related('users__user').order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment.id,
                'comment': comment.comment,
                'created_at': comment.created_at,
                'user__name': comment.users.user.username if comment.users.user else 'Пользователь'
            })
        
        return JsonResponse({'comments': comments_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
"""Рендер профиля авторизованного пользователя"""
@login_required
def profile(request):
    user = request.user
    auth_user = User.objects.get(id=user.id)
    if auth_user.is_superuser:
        patterns = Patterns.objects.all().order_by('-id')
    else:
        profile = Profiles.objects.get(user=user)
        fav = Favorites.objects.filter(users=profile).order_by('-id')
        patterns = [f.patterns for f in fav]
    return render(request, 'test/account.html', {"patterns": patterns})

"""API для удаления паттерна по id"""
@login_required
@csrf_exempt
def delete_pattern_api(request, id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        user = request.user
        auth_user = User.objects.get(id=user.id)
        
        if not auth_user.is_superuser:
            return JsonResponse({'error': 'Доступ запрещен'}, status=403)
        
        pattern = get_object_or_404(Patterns, id=id)
        title = pattern.title
        
        pattern.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Паттерн "{title}" успешно удален'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
"""Рендер эдитера либо пустого либо если есть id редактор существующего"""
@login_required
def editor(request, id=None):
    user = request.user
    auth_user = User.objects.get(id=user.id)
    if not auth_user.is_superuser:
        return redirect('/')
    
    pattern = None
    if id:
        pattern = get_object_or_404(Patterns, id=id)
    
    categories = Categories.objects.all()
    tags = Tags.objects.all()
    stacks = Stacks.objects.all()
    
    selected_tag_ids = []
    selected_stack_ids = []
    if pattern:
        selected_tag_ids = list(pattern.tags.values_list('id', flat=True))
        selected_stack_ids = list(pattern.stacks.values_list('id', flat=True))
    
    context = {
        'categories': categories,
        'tags': tags,
        'stacks': stacks,
        'pattern': pattern,
        'selected_tag_ids': selected_tag_ids,
        'selected_stack_ids': selected_stack_ids,
    }
    
    return render(request, 'test/editor.html', context)

"""API для создания тега"""
@login_required
@csrf_exempt
def create_tag_api(request):
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({'error': 'Имя тега обязательно'}, status=400)
        
        tag, created = Tags.objects.get_or_create(name=name)
        
        return JsonResponse({
            'success': True,
            'id': tag.id,
            'name': tag.name,
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

"""API для создания стека"""
@login_required
@csrf_exempt
def create_stack_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({'error': 'Имя стека обязательно'}, status=400)
        
        stack, created = Stacks.objects.get_or_create(name=name)
        
        return JsonResponse({
            'success': True,
            'id': stack.id,
            'name': stack.name,
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

"""API для создания категории"""
@login_required
@csrf_exempt
def create_category_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        
        if not title:
            return JsonResponse({'error': 'Название категории обязательно'}, status=400)
        
        category, created = Categories.objects.get_or_create(title=title)
        
        return JsonResponse({
            'success': True,
            'id': category.id,
            'title': category.title,
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

"""API для создания паттерна"""
@login_required
@csrf_exempt
def create_pattern_api(request):
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        pattern = Patterns.objects.create(
            title=data.get('title'),
            term=data.get('term', ''),
            categories_id=data.get('category'),
            problem=data.get('problem', ''),
            solution=data.get('solution', ''),
            examples=data.get('examples', ''),
            consclusions=data.get('consclusions', '')
        )
        
        tag_ids = data.get('tags', [])
        if tag_ids:
            pattern.tags.set(tag_ids)
        
        stack_ids = data.get('stacks', [])
        if stack_ids:
            pattern.stacks.set(stack_ids)
        
        Ratings.objects.update_or_create(patterns=pattern)
        Logs.objects.update_or_create(patterns=pattern)
        
        return JsonResponse({
            'success': True,
            'message': f'Паттерн "{pattern.title}" успешно создан!',
            'pattern_id': pattern.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

"""API для обновления паттерна"""
@login_required
@csrf_exempt
def update_pattern_api(request, id):
    
    if request.method != 'PUT' and request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        pattern = get_object_or_404(Patterns, id=id)
        data = json.loads(request.body)
        
        # Обновляем поля
        pattern.title = data.get('title', pattern.title)
        pattern.term = data.get('term', pattern.term)
        pattern.categories_id = data.get('category', pattern.categories_id)
        pattern.problem = data.get('problem', pattern.problem)
        pattern.solution = data.get('solution', pattern.solution)
        pattern.examples = data.get('examples', pattern.examples)
        pattern.consclusions = data.get('consclusions', pattern.consclusions)
        pattern.save()
        
        # Обновляем теги
        tag_ids = data.get('tags', [])
        if tag_ids:
            pattern.tags.set(tag_ids)
        else:
            pattern.tags.clear()
        
        # Обновляем стеки
        stack_ids = data.get('stacks', [])
        if stack_ids:
            pattern.stacks.set(stack_ids)
        else:
            pattern.stacks.clear()
        
        Ratings.objects.update_or_create(patterns=pattern)
        Logs.objects.update_or_create(patterns=pattern)
        return JsonResponse({
            'success': True,
            'message': f'Паттерн "{pattern.title}" успешно обновлен!',
            'pattern_id': pattern.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


"""Выход из аккаунта"""
@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('/')

"""Регистрация"""
def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'registration/reg.html', {"form": form})