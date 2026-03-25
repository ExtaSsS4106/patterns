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
    return render(request, 'test/index.html', {"categories": categories})

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
def editor(request):
    """Страница редактора"""
    categories = Categories.objects.all()
    tags = Tags.objects.all()
    stacks = Stacks.objects.all()
    
    context = {
        'categories': categories,
        'tags': tags,
        'stacks': stacks,
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
