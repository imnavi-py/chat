import json
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.views import View

from chat.forms import GroupSearchForm, UserLoginForm, UserProfileForm, UserRegistrationForm
from chat.utils import convert_to_ascii
from .models import Group, Message, UserProfile

from django.shortcuts import render, redirect
from .models import Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




# @login_required(login_url = 'chat/login.html')
# views.py
def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # برای سوپر یوزر، همه گروه‌ها را دریافت کن
            groups = Group.objects.all()
        else:
            # برای کاربران عادی، فقط گروه‌های عمومی یا گروه‌هایی که کاربر عضو است
            groups = Group.objects.filter(Q(type='public') | Q(members=request.user))

        search_form = GroupSearchForm(request.GET or None)
        if search_form.is_valid():
            search_term = search_form.cleaned_data['search_term']
            groups = groups.filter(name__icontains=search_term)

        return render(request, 'chat/index.html', {'groups': groups, 'search_form': search_form})
    else:
        return redirect('login')



@login_required
def create_group(request):
    if request.method == 'POST':
        if request.user.is_superuser:
            group_name = request.POST.get('group_name')
            slug = request.POST.get('slug')  # نامک را از درخواست بگیر
            group_type = request.POST.get('type')  # اصلاح نام فیلد
            ascii_group_name = convert_to_ascii(group_name)


             # تبدیل نام گروه به ASCII اگر نامک خالی باشد
            if not slug:
                slug = convert_to_ascii(group_name)  # نامک را از نام گروه تولید کن

            # بررسی وجود گروه با نام مشابه
            if Group.objects.filter(name=group_name).exists():
                error_message = "این نام گروه قبلاً استفاده شده است."
                return render(request, 'chat/create_group.html', {'error_message': error_message})
            
             # بررسی وجود نامک مشابه
            if Group.objects.filter(slug=slug).exists():
                error_message = "این نامک قبلاً استفاده شده است."
                return render(request, 'chat/create_group.html', {'error_message': error_message})

            # ایجاد گروه
            group = Group.objects.create(name=group_name,slug=convert_to_ascii(slug), created_by=request.user, type=group_type)  
            group.members.add(request.user)
            # return redirect('chat:index')  
            # return redirect('group_chat', group_name=group.name)
            return redirect('group_chat', slug=group.slug)
        else:
            error_message = "شما اجازه ایجاد گروه را ندارید."
            return render(request, 'chat/create_group.html', {'error_message': error_message})

    return render(request, 'chat/create_group.html')



@login_required
def delete_group(request, group_slug):
    if request.user.is_superuser:
        group = get_object_or_404(Group, slug=group_slug)
        group.delete()  # حذف گروه
        return redirect('index')  # هدایت به صفحه اصلی
    else:
        return render(request, 'chat/error.html', {'error_message': 'شما اجازه حذف گروه را ندارید.'})




@login_required
def group_chat(request, slug):
    group = get_object_or_404(Group, slug=slug)
    messages = Message.objects.filter(group=group).order_by('timestamp')
    members = group.members.all()
    all_users = User.objects.exclude(id__in=members.values_list('id', flat=True))

    # اضافه کردن کاربر جدید
    if request.method == 'POST' and 'add_member' in request.POST:
        username = request.POST.get('username')
        user_to_add = User.objects.get(username=username)
        group.members.add(user_to_add)
        return redirect('group_chat', slug=slug)

    user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'chat/group_chat.html', {
        'group': group,
        'messages': messages,
        'members': members,
        'all_users': all_users,
        'user_profile': user_profile,
    })



def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # تغییر به آدرس مناسب
    else:
        form = UserLoginForm()
    
    return render(request, 'chat/login.html', {'form': form})  # ارسال فرم به قالب



def logout_view(request):
    logout(request)  # خروج کاربر
    return redirect('login')  # هدایت به صفحه لاگین یا هر صفحه دیگری



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()  # ذخیره کاربر جدید
                UserProfile.objects.create(user=user)  # ایجاد پروفایل کاربر
                return redirect('login')  # تغییر به آدرس مناسب
            except IntegrityError:
                form.add_error('username', 'این نام کاربری قبلاً استفاده شده است.')
    else:
        form = UserRegistrationForm()
    return render(request, 'chat/register.html', {'form': form})



@login_required
def profile_view(request):
    # دریافت پروفایل کاربر، در صورت عدم وجود، ایجاد می‌کند
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # تغییر به آدرس مناسب
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'chat/profile.html', {
        'form': form,
        'user_profile': user_profile,  # ارسال پروفایل کاربر به قالب
        'user': request.user  # ارسال کاربر به قالب
    })


@login_required
def chat_view(request, group_name):
    return render(request, 'chat.html', {'group_name': group_name})

@login_required
def private_chat_view(request, username):
    user_to_chat = get_object_or_404(User, username=username)
    return render(request, 'chat/private_chat.html', {'user_to_chat': user_to_chat})





 


