from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:title>/', views.catalog, name='catalog'),
    path('pattern/<int:id>/', views.pattern_detail, name='pattern_detail'),
    path('editor/', views.editor, name='editor'),
    
    # API для динамического добавления
    path('api/tags/create/', views.create_tag_api, name='create_tag_api'),
    path('api/stacks/create/', views.create_stack_api, name='create_stack_api'),
    path('api/categories/create/', views.create_category_api, name='create_category_api'),
    path('api/patterns/create/', views.create_pattern_api, name='create_pattern_api'),
    
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout', views.logout_view, name='logout'),
]