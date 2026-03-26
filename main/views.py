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
def index(request):
    categories = Categories.objects.all()
    patterns = Patterns.objects.all()
    return render(request, 'test/index.html', {"categories": categories, "patterns":patterns})

def catalog(request, title):
    category = get_object_or_404(Categories, title=title)
    if category.title == title:
        patterns = Patterns.objects.filter(categories=category)
        return render(request, 'test/catalog.html', {"patterns": patterns})
    return render(request, 'test/catalog.html', {"patterns": "None"})

def pattern_detail(request, id):
    pattern = get_object_or_404(Patterns, id=id)
    return render(request, 'test/pattern-detail.html', {"pattern": pattern})

@login_required
def add_comment(request):
    """API для добавления комментария"""
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


@csrf_exempt
def select_comments(request):
    """API для получения комментариев"""
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

@login_required
@csrf_exempt
def delete_pattern_api(request, id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        user = request.user
        auth_user = User.objects.get(id=user.id)
        
        # Проверяем права доступа
        if not auth_user.is_superuser:
            return JsonResponse({'error': 'Доступ запрещен'}, status=403)
        
        pattern = get_object_or_404(Patterns, id=id)
        title = pattern.title
        
        # Удаляем паттерн
        pattern.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Паттерн "{title}" успешно удален'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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

@login_required
@csrf_exempt
def create_tag_api(request):
    """API для создания тега"""
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

@login_required
@csrf_exempt
def create_stack_api(request):
    """API для создания стека"""
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

@login_required
@csrf_exempt
def create_category_api(request):
    """API для создания категории"""
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

@login_required
@csrf_exempt
def create_pattern_api(request):
    """API для создания паттерна"""
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
        
        return JsonResponse({
            'success': True,
            'message': f'Паттерн "{pattern.title}" успешно создан!',
            'pattern_id': pattern.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@csrf_exempt
def update_pattern_api(request, id):
    """API для обновления паттерна"""
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
        
        return JsonResponse({
            'success': True,
            'message': f'Паттерн "{pattern.title}" успешно обновлен!',
            'pattern_id': pattern.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('/')

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