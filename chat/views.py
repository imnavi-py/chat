import json
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.views import View

from chat.forms import GroupSearchForm, UserLoginForm, UserProfileForm, UserRegistrationForm
from chat.utils import convert_to_ascii, set_auth_cookie
from chatapp.lib.ApiResponse import ApiResponse
from .models import Group, Message, PrivateGroup, PrivateMessage, UserProfile

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
from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


from .models import Group, Message, UserProfile
from .serializers import MemberSerializer, MessageSerializer, PrivateGroupSerializer, UserProfileSerializer
from django.utils.translation import gettext_lazy as _

# @login_required(login_url = 'chat/login.html')
# views.py
def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # برای سوپر یوزر، همه گروه‌ها را دریافت کن
            groups = Group.objects.all()
            private_groups = PrivateGroup.objects.all()  # گروه‌های خصوصی برای سوپر یوزر
        else:
            # برای کاربران عادی، فقط گروه‌های عمومی یا گروه‌هایی که کاربر عضو است
            groups = Group.objects.filter(Q(type='public') | Q(members=request.user))
            private_groups = PrivateGroup.objects.filter(members=request.user)  # گروه‌های خصوصی که کاربر عضو است

        search_form = GroupSearchForm(request.GET or None)
        if search_form.is_valid():
            search_term = search_form.cleaned_data['search_term']
            groups = groups.filter(name__icontains=search_term)
            private_groups = private_groups.filter(name__icontains=search_term)  # جستجو برای گروه‌های خصوصی

        # بررسی شرط و تنظیم مقدار `pv_url` برای هر گروه خصوصی
        current_username = request.user.username
        for private_group in private_groups:
            # اگر نام کاربری فعلی برابر با target_user باشد
            if private_group.target_user.username == current_username:
                private_group.pv_url = private_group.created_by.username  # مقدار pv_url را برابر با created_by.username قرار می‌دهیم
                private_group.save()  # تغییرات را ذخیره می‌کنیم

        # ارسال داده‌ها به قالب
        return render(request, 'chat/index.html', {
            'groups': groups,
            'private_groups': private_groups,
            'search_form': search_form
        })
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
        if 'add_member' in request.POST:
            username = request.POST.get('username')
            user_to_add = User.objects.get(username=username)
            group.members.add(user_to_add)
            return redirect('group_chat', slug=slug)
    
        elif 'send_private_message' in request.POST:  # بررسی ارسال پیام خصوصی
            target_username = request.POST.get('target_username')
            message = request.POST.get('message')
            target_user = User.objects.get(username=target_username)
            return redirect('private_chat', target_username=target_username)

    user_profile = UserProfile.objects.get(user=request.user)

    return render(request, 'chat/group_chat.html', {
        'group': group,
        'messages': messages,
        'members': members,
        'all_users': all_users,
        'user_profile': user_profile,
    })


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(username=username)
                # بررسی رمز عبور (در صورت استفاده از رمز عبور هش شده)
                if user.check_password(password):
                    login(request, user)
                    return redirect('index')  # تغییر به آدرس مناسب
                else:
                    form.add_error(None, 'نام کاربری یا رمز عبور نادرست است.')
            except User.DoesNotExist:
                form.add_error(None, 'نام کاربری یا رمز عبور نادرست است.')

    else:
        form = UserLoginForm()

    return render(request, 'chat/login.html', {'form': form})  # ارسال فرم به قالب # ارسال فرم به قالب



def logout_view(request):
    logout(request)  # خروج کاربر
    return redirect('login')  # هدایت به صفحه لاگین یا هر صفحه دیگری


@csrf_exempt
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
def private_chat_view(request, target_username):
    current_username = request.user.username  # نام کاربر فعلی
    target_user = get_object_or_404(User, username=target_username)  # بررسی وجود کاربر هدف
    return render(request, 'chat/chat_private.html', {
        'username': current_username,
        'target_username': target_username,
        'target_user': target_user,  # ارسال پروفایل کاربر هدف به قالب
    })


def private_chat(request, username):
    return render(request, 'chat/chat_private.html', {'username': username})


AUTH_TOKEN_VALIDITY = 604800  # 7 روز
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # احراز هویت کاربر
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # توکن را تولید یا دریافت کنید
            token, created = Token.objects.get_or_create(user=user)

            # تنظیم کوکی
            expires_at = datetime.utcnow() + timedelta(seconds=AUTH_TOKEN_VALIDITY)
            response = Response({f"message: Login successful, token : {token.key}" }, status=status.HTTP_200_OK)
            response.set_cookie(
                key='token',
                value=token.key,
                httponly=True,
                secure=False,
                samesite='None',  # یا 'Lax' یا 'Strict' بسته به نیاز شما
                expires=expires_at,
                domain='.nargil.co'
            )
            return response
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

    def group_chat_view(request, group_slug):
        group = get_object_or_404(Group, slug=group_slug)
        messages = PrivateMessage.objects.filter(group=group).order_by('-timestamp')  # یا ترتیب دلخواه دیگر

        return render(request, 'chat/group_chat.html', {'group': group, 'messages': messages})
    







    ##API

tokenAccess = "00a289d2fabae9baacbb83eeb47d7cb5e3197317"
def get_user_from_token(self, token):
        try:
            # فرض می‌کنیم توکن یک شناسه کاربر است
            user = User.objects.get(auth_token=token)  # یا شناسه کاربر
            if user.is_active:
                return user
            else:
                raise AuthenticationFailed('کاربر غیرفعال است.')
        except User.DoesNotExist:
            raise AuthenticationFailed('کاربر یافت نشد.')
        
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Group
from .utils import convert_to_ascii  # فرض کنید این تابع برای تبدیل به ASCII است
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
        
def authenticate_user_with_token(token):
    try:
        # فرض می‌کنیم توکن به عنوان ID کاربر است
        user = User.objects.get(id=token)
        
        if user.is_active:  # بررسی کنید که کاربر فعال باشد
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
            }
        else:
            raise AuthenticationFailed('کاربر غیرفعال است.')
    
    except User.DoesNotExist:
        raise AuthenticationFailed('کاربر یافت نشد.')
    
class CreateGroupAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    authentication_classes = []
    # tokenAccess = "00a289d2fabae9baacbb83eeb47d7cb5e3197317"
    def get_user_from_token(self, token):
            try:
                # فرض می‌کنیم توکن یک شناسه کاربر است
                user = User.objects.get(auth_token=token)  # یا شناسه کاربر
                if user.is_active:
                    return user
                else:
                    raise AuthenticationFailed('کاربر غیرفعال است.')
            except User.DoesNotExist:
                raise AuthenticationFailed('کاربر یافت نشد.')
    
        
    def post(self, request):

        # توکن ثابت برای تست
        

        # احراز هویت کاربر با توکن ثابت
        try:
            self.user = self.get_user_from_token(tokenAccess)
            print(self.user.is_superuser)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        if not self.user.is_superuser:
            return Response({"error": "شما اجازه ایجاد گروه را ندارید."}, status=status.HTTP_403_FORBIDDEN)
            
        group_name = request.data.get('group_name')
        slug = request.data.get('slug')
        group_type = request.data.get('type')

        ascii_group_name = convert_to_ascii(group_name)

        if not slug:
            slug = convert_to_ascii(group_name)

        # بررسی وجود گروه با نام مشابه
        if Group.objects.filter(name=group_name).exists():
            return Response({"error": "این نام گروه قبلاً استفاده شده است."}, status=status.HTTP_400_BAD_REQUEST)

        # بررسی وجود نامک مشابه
        if Group.objects.filter(slug=slug).exists():
            return Response({"error": "این نامک قبلاً استفاده شده است."}, status=status.HTTP_400_BAD_REQUEST)

        # ایجاد گروه
        group = Group.objects.create(name=group_name, slug=convert_to_ascii(slug), created_by=self.user, type=group_type)
        group.members.add(self.user)
        print(group.created_by.username,)

        # پاسخ با اطلاعات گروه جدید
        response_data = {
            "id": group.id,
            "name": group.name,
            "slug": group.slug,
            "created_by": group.created_by.username,
            "type": group.type,
            "members_count": group.members.count(),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    


class ListGroupsAPIView(APIView):
    # tokenAccess = "00a289d2fabae9baacbb83eeb47d7cb5e3197317"
    def get_user_from_token(self, token):
            try:
                # فرض می‌کنیم توکن یک شناسه کاربر است
                user = User.objects.get(auth_token=token)  # یا شناسه کاربر
                if user.is_active:
                    return user
                else:
                    raise AuthenticationFailed('کاربر غیرفعال است.')
            except User.DoesNotExist:
                raise AuthenticationFailed('کاربر یافت نشد.')
    def get(self, request):
        # دریافت پارامتر type از درخواست
        group_type = request.query_params.get('type', None)

        # بررسی نوع گروه دریافتی
        if group_type == 'Group':
            # اگر نوع Group ارسال شد
            groups = Group.objects.all()
        elif group_type == 'PrivateGroup':
            # اگر نوع PrivateGroup ارسال شد
            groups = PrivateGroup.objects.all()
        else:
            # اگر هیچ پارامتر type ارسال نشده یا نوع دیگری ارسال شده، تمام گروه‌ها از Group بازیابی می‌شود
            groups = Group.objects.all()

        # ساخت لیست از گروه‌ها
        group_list = []

        for group in groups:
            group_data = {
                "id": group.id,
                "name": group.name,
                "slug": group.slug,
                "created_by": group.created_by.username,
                "members_count": group.members.count(),
                
                
            }
            
            # اگر گروه از نوع PrivateGroup باشد، فیلد 'type' را نمایش ندهید
            if isinstance(group, PrivateGroup):
                selfuser = self.get_user_from_token(tokenAccess)
                selfuser_username = selfuser.username if hasattr(selfuser, 'username') else ""
                group_data["target_user"] = group.target_user.username if group.target_user else None
                getpv = ""
                    #  print(group.target_user.username==selfuser_username)
                if group.target_user.username == selfuser_username:
                    print("yes")
                    group.pv_url = group.created_by.username

                    print(group.pv_url)
                group_data["pv_url"] = group.pv_url

    
                
                # حذف فیلد 'type' برای PrivateGroup
                group_list.append(group_data)
            else:
                # در غیر این صورت، فیلد 'type' را اضافه کن
                group_data["type"] = group.type
                group_list.append(group_data)

        # ارسال داده‌ها به عنوان Response
        return Response(group_list, status=status.HTTP_200_OK)
    


class GroupChatAPIView(APIView):


    def post(self, request, slug):
        group = get_object_or_404(Group, slug=slug)

        # اضافه کردن کاربر جدید
        if 'add_member' in request.data:
            username = request.data.get('username')
            try:
                user_to_add = User.objects.get(username=username)
                group.members.add(user_to_add)
                return Response({"message": f"{username} به گروه اضافه شد."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        

         # حذف کاربر از گروه
        elif 'remove_member' in request.data:
            username = request.data.get('username')
            try:
                user_to_remove = User.objects.get(username=username)
                group.members.remove(user_to_remove)
                return Response({"message": f"{username} از گروه حذف شد."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            

        # ارسال پیام خصوصی
        elif 'send_private_message' in request.data:
            target_username = request.data.get('target_username')
            message_content = request.data.get('message')
            try:
                target_user = User.objects.get(username=target_username)
                # اینجا می‌توانید پیام را ذخیره کنید
                Message.objects.create(group=group, sender=request.user, content=message_content)
                return Response({"message": "پیام خصوصی ارسال شد."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "عملیات نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)
    




@api_view(['GET'])
def group_chat_api(request, slug):
    token = tokenAccess  # یا از request.headers.get('Authorization') استفاده کنید

    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return Response({"error": "Invalid token."}, status=status.HTTP_403_FORBIDDEN)

    group = get_object_or_404(Group, slug=slug)
    messages = Message.objects.filter(group=group).order_by('timestamp')
    members = group.members.all()  # دریافت اعضا
    all_users = User.objects.exclude(id__in=members.values_list('id', flat=True))
    user_profile = UserProfile.objects.get(user=user)

    # ساخت داده‌ها با استفاده از MemberSerializer
    members_data = []
    for member in members:
        user_profile = UserProfile.objects.get(user=member)  # دریافت UserProfile مرتبط
        members_data.append({
            'id': user_profile.id,
            'username': user_profile.user.username,
            'is_superuser': user_profile.user.is_superuser,
        })

    all_users_data = [{'id': user.id, 'username': user.username} for user in all_users]

    data = {
        'group': {
            'id': group.id,
            'name': group.name,
            'slug': group.slug,
            'type': group.type,
            'members': members_data,  # باید اطلاعات کامل اعضا را برگرداند
        },
        'messages': MessageSerializer(messages, many=True).data,
        'all_users': all_users_data,
        'user_profile': UserProfileSerializer(user_profile).data,
    }

    return Response(data)


## Private Group
@api_view(['GET'])
def private_chat_api(request, slug):
    print("test")
    # token = request.headers.get('Authorization', '').replace('Token ', '')
    token = tokenAccess

    # بررسی توکن و کاربر
    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return Response({"error": "Invalid token."}, status=status.HTTP_403_FORBIDDEN)

    # بازیابی گروه خصوصی با توجه به نامک
    private_group = get_object_or_404(PrivateGroup, slug=slug)
    
    # بررسی اینکه آیا کاربر جزو اعضای گروه است یا نه
    if user not in private_group.members.all():
        return Response({"error": "You are not a member of this private chat group."}, status=status.HTTP_403_FORBIDDEN)
    
    # سریالایزر گروه خصوصی با پیام‌ها و اعضا
    private_group_data = PrivateGroupSerializer(private_group).data
    
    return Response({"private_group": private_group_data})


## Get All Users Data

@api_view(['GET'])
def all_users_with_groups_api(request):
    # دریافت تمام کاربران
    all_users = User.objects.all()

    # آماده‌سازی داده‌ها با اطلاعات گروه‌ها
    all_users_data = []
    for user in all_users:
        user_profile = UserProfile.objects.get(user=user)  # دریافت UserProfile مرتبط
        groups = user.group_members.all()  # دریافت گروه‌هایی که کاربر عضو آن‌هاست
        groups_data = [{'id': group.id, 'name': group.name, 'slug': group.slug, 'type': group.type} for group in groups]

        all_users_data.append({
            'id': user_profile.id,
            'username': user.username,
            'is_superuser': user.is_superuser,
            'groups': groups_data  # لیست گروه‌ها
        })

    return Response({"all_users": all_users_data}, status=status.HTTP_200_OK)



## User Profile

class UserProfileAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # احراز هویت برای کاربران لاگین‌کرده
    
    def get(self, request):

        token = tokenAccess  # یا از request.headers.get('Authorization') استفاده کنید

        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_403_FORBIDDEN)
        # دریافت پروفایل کاربر یا ایجاد آن در صورت عدم وجود
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user_profile)
        return ApiResponse.success(self, _("User Profile Founded"), serializer.data, status.HTTP_200_OK)

    def post(self, request):
        token = tokenAccess  # یا از request.headers.get('Authorization') استفاده کنید

        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_403_FORBIDDEN)
        
        # دریافت یا ایجاد پروفایل کاربر
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return ApiResponse.success(self, _("UserProfile Updated"),serializer.data, status.HTTP_200_OK)
        return ApiResponse.error(self, _("Something went wrong!"),serializer.errors, status.HTTP_400_BAD_REQUEST)
    







@login_required
def private_group_chat(request, slug):
    private_group = get_object_or_404(PrivateGroup, slug=slug)
    
    # بررسی اینکه کاربر عضو این گروه خصوصی است
    if request.user not in private_group.members.all():
        return redirect('index')  # اگر کاربر عضو گروه نیست، هدایت به صفحه اصلی
    
    # اگر کاربر عضو است، پیام‌ها و اعضای گروه را نمایش می‌دهیم
    messages = private_group.messages.all().order_by('timestamp')  # یا به ترتیب مورد نظر شما
    return render(request, 'chat/private_group_chat.html', {
        'private_group': private_group,
        'messages': messages,
    })
