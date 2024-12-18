from django.conf import settings
from django.urls import path

from chat import consumers
from . import views
from .views import CreateGroupAPIView, GroupChatAPIView, ListGroupsAPIView, LoginView, UserProfileAPIView, delete_group, group_chat_api, login_view, logout_view,   register_view, profile_view
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('create_group/', views.create_group, name='create_group'),
    # path('group/<str:group_name>/', views.group_chat, name='group_chat'),
    path('group/<slug:slug>/', views.group_chat, name='group_chat'),  # استفاده از نامک

    path('delete_group/<str:group_slug>/', delete_group, name='delete_group'),  # URL برای حذف گروه
    # path('chat/private/<str:username>/', private_chat_view, name='private_chat'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # مسیر خروج
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    # path('chat/private/<str:username>/', views.private_chat, name='private_chat'),
    path('chat/private/<str:target_username>/', views.private_chat_view, name='private_chat'),

    path('api-token-auth/', LoginView.as_view(), name='api_token_auth'),

    ##API

    path('api/groups/create/', CreateGroupAPIView.as_view(), name='create_group_api'),
    path('api/groups/', ListGroupsAPIView.as_view(), name='list_groups'),
    path('api/group_chat/<slug:slug>/', GroupChatAPIView.as_view(), name='group_chat_api'),
    path('api/groups/<slug:slug>/chat/', group_chat_api, name='group_chat_api'),

    path('api/users-info/', views.all_users_with_groups_api, name='all_users_with_groups'),
    path('api/user/profile/', UserProfileAPIView.as_view(), name='user_profile_api'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
