from django.conf import settings
from django.urls import path
from . import views
from .views import delete_group, login_view, logout_view, register_view, profile_view
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('create_group/', views.create_group, name='create_group'),
    # path('group/<str:group_name>/', views.group_chat, name='group_chat'),
    path('group/<slug:slug>/', views.group_chat, name='group_chat'),  # استفاده از نامک
    path('private/<str:username>/', views.private_chat, name='private_chat'),
    path('delete_group/<str:group_slug>/', delete_group, name='delete_group'),  # URL برای حذف گروه


    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # مسیر خروج
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
