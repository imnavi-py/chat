from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404

from chat.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from .models import Group, Message, UserProfile

from django.shortcuts import render, redirect
from .models import Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect

# @login_required(login_url = 'chat/login.html')
def index(request):
    groups = Group.objects.all()
    print("test")
    if not request.user.is_authenticated:
        return redirect('login')  # هدایت به صفحه ورود
    else:
        return render(request, 'chat/index.html', {'groups': groups})



@login_required
def create_group(request):
    
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        Group.objects.create(name=group_name)
        return redirect('index')
    return render(request, 'chat/create_group.html')



@login_required
def group_chat(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    messages = Message.objects.filter(group=group).order_by('timestamp')  # دریافت پیام‌ها به ترتیب زمان

    if request.user.is_authenticated:
        return render(request, 'chat/group_chat.html', {'group': group, 'messages': messages})
    else:
        return render(request, 'login')



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
