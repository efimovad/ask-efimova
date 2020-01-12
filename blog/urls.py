from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve


urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('profile/', views.update_profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('like/', views.like_post, name='like_post'),
    path('dislike/', views.dislike_post, name='dislike_post'),
    path('posts/tag/<int:pk>/', views.posts_by_tag, name='posts_by_tag'),
]

