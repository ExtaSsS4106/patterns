from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/<str:title>/', views.catalog, name='catalog'),
    path('pattern/<int:id>/', views.pattern_detail, name='pattern_detail'),
    path('editor/', views.editor, name='editor'),
    path('editor/<int:id>/', views.editor, name='editor_edit'),
    path('profile/', views.profile, name='profile'),
    
    # API для комментариев
    path('add_comment/', views.add_comment, name='add_comment'),
    path('select_comments/', views.select_comments, name='select_comments'),
    
    # API для тегов, стеков, категорий
    path('api/tags/create/', views.create_tag_api, name='create_tag_api'),
    path('api/stacks/create/', views.create_stack_api, name='create_stack_api'),
    path('api/categories/create/', views.create_category_api, name='create_category_api'),
    path('api/patterns/create/', views.create_pattern_api, name='create_pattern_api'),
    path('api/patterns/update/<int:id>/', views.update_pattern_api, name='update_pattern_api'),
    path('api/patterns/delete/<int:id>/', views.delete_pattern_api, name='delete_pattern_api'),
    path('api/set_dislike/', views.set_dislike, name='set_dislike'),
    path('api/set_like/', views.set_like, name='set_like'),
    path('api/check_favorite/', views.check_favorite, name='check_favorite'),
    path('api/get_ratings/', views.get_ratings, name='get_ratings'),
    
    path('sign-up/', views.sign_up, name='sign_up'),
    path('logout/', views.logout_view, name='logout'),
]