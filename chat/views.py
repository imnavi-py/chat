

from uuid import UUID
import uuid
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
import httpx


from chat.forms import GroupSearchForm, UserLoginForm, UserProfileForm, UserRegistrationForm
from chat.serializers import PrivateGroupSerializer
from chat.utils import convert_to_ascii
from config.lib.ApiResponse import ApiResponse
from config.lib.api import get_info
from config.lib.setting import API
from .models import BaseUser, Group, Message, PrivateGroup, PrivateMessage, UserProfile
from django.shortcuts import render, redirect
from .models import Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from .models import Group, Message, UserProfile
from .serializers import  MessageSerializer, UserProfileSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Group
from .utils import convert_to_ascii  # فرض کنید این تابع برای تبدیل به ASCII است
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed

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

tokenAccess = "868af6b0f862d5e91553a3202ed7a923b825cd97"
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
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "برای ایجاد گروه باید وارد سیستم شوید."}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = BaseUser.objects.get(id=request.user.id)  # بارگیری کاربر به عنوان نمونه BaseUser

        # if not user.is_superuser:
        #     return Response({"error": "شما اجازه ایجاد گروه را ندارید."}, status=status.HTTP_403_FORBIDDEN)
        
        group_name = request.data.get('group_name')
        slug = request.data.get('slug') or convert_to_ascii(group_name)
        group_type = request.data.get('type')

        if Group.objects.filter(name=group_name).exists():
            return Response({"error": "این نام گروه قبلاً استفاده شده است."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Group.objects.filter(slug=slug).exists():
            return Response({"error": "این نامک قبلاً استفاده شده است."}, status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.create(name=group_name, slug=slug, created_by=user, type=group_type)
        group.members.add(user)

        response_data = {
            "id": group.id,
            "name": group.name,
            "slug": group.slug,
            "created_by": group.created_by.first_name_fa + group.created_by.last_name_fa,
            "type": group.type,
            "members_count": group.members.count(),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    


class ListGroupsAPIView(APIView):
    def get(self, request):
        # بررسی اینکه آیا کاربر احراز هویت شده است یا خیر
        if not request.user.is_authenticated:
            return Response({"error": "برای مشاهده گروه‌ها باید وارد سیستم شوید."}, status=status.HTTP_401_UNAUTHORIZED)

        group_type = request.query_params.get('type', None)

        # فیلتر کردن گروه‌ها بر اساس نوع
        if group_type == 'Group':
            groups = Group.objects.all()
        elif group_type == 'PrivateGroup':
            groups = PrivateGroup.objects.all()
        else:
            groups = Group.objects.all() 

        group_list = []
        for group in groups:
            # بررسی اینکه آیا کاربر عضو گروه است یا نه
            if isinstance(group, PrivateGroup):
                # برای گروه‌های خصوصی بررسی می‌کنیم که آیا کاربر در فیلدهای created_by یا target_user قرار دارد
                if group.created_by.id == request.user.id or (group.target_user and group.target_user.id == request.user.id):
                    group_data = {
                        "id": group.id,
                        "name": group.name,
                        "slug": group.slug,
                    }
                    
                    user_name = ""
                    # اطلاعات اضافی برای گروه‌های خصوصی
                    group_data["created_by"] = group.created_by.first_name_fa +" "+ group.created_by.last_name_fa
                    group_data["target_user"] = group.target_user.first_name_fa +" "+ group.target_user.last_name_fa if group.target_user else None
                    group_data["members_count"] = group.members.count()
                    if request.user.first_name_fa == group.created_by.first_name_fa:
                        user_name = group.target_user.first_name_fa +" "+ group.target_user.last_name_fa
                    else:
                        user_name =  group.created_by.first_name_fa +" "+ group.created_by.last_name_fa

                    group_data["user_name"] = user_name
                    
                    group_list.append(group_data)

            elif isinstance(group, Group):
                # برای گروه‌های عمومی بررسی می‌کنیم که آیا کاربر عضو گروه است
                if group.members.filter(id=request.user.id).exists():
                    group_data = {
                        "id": group.id,
                        "name": group.name,
                        "slug": group.slug,
                        "created_by": group.created_by.first_name_fa +" "+ group.created_by.last_name_fa,
                        "members_count": group.members.count(),
                    }
                    group_list.append(group_data)

        return Response(group_list, status=status.HTTP_200_OK)
    


class GroupChatAPIView(APIView):


    def post(self, request, slug):
        # بررسی وجود گروه با نام (slug) مشخص شده
        group = get_object_or_404(Group, slug=slug)

        # دریافت uuid کاربر از درخواست و اعتبارسنجی آن
        user_uuid = request.data.get('uuid')
        
        # بررسی اینکه uuid ارسال شده و معتبر باشد
        if not user_uuid:
            return Response({"error": "UUID کاربر ارسال نشده است."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # تبدیل مقدار uuid به یک شیء UUID
            user_uuid = UUID(user_uuid)
            # یافتن کاربر بر اساس uuid
            user = BaseUser.objects.get(id=user_uuid)
        except (ValueError, TypeError):
            return Response({"error": "UUID معتبر نیست."}, status=status.HTTP_400_BAD_REQUEST)
        except BaseUser.DoesNotExist:
            return Response({"error": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        # بررسی عملیات افزودن یا حذف کاربر از گروه
        if request.data.get('action') == 'add_member':
            # اضافه کردن کاربر به گروه
            group.members.add(user)
            user_data = {
                "id": str(user.id),
                "nationalcode": user.nationalcode,
                "first_name_fa": user.first_name_fa,
                "last_name_fa": user.last_name_fa,
                "usr_avatar": user.usr_avatar
            }
            return Response({
                "message": f"کاربر با نام {user.first_name_fa + user.last_name_fa} به گروه {group.name} اضافه شد.",
                "user": user_data
            }, status=status.HTTP_200_OK)

        elif request.data.get('action') == 'remove_member':
            # حذف کاربر از گروه
            group.members.remove(user)
            return Response({
                "message": f"کاربر با کد ملی {user.first_name_fa + user.last_name_fa} از گروه {group.name} حذف شد."
            }, status=status.HTTP_200_OK)

        # اگر هیچ کدام از پارامترهای add_member یا remove_member موجود نباشد
        return Response({"error": "پارامتر add_member یا remove_member ارسال نشده است."}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def save_user_data(request):
    # ابتدا بررسی می‌کنیم که کاربر احراز هویت شده باشد
    print("this is:",request.user)
    if request.user.is_authenticated:
        # پرینت کردن مقدار request.user برای بررسی داده‌ها
        print("User Data:", request.user)
        print("User Avatar:", request.user.avatar_url)

        # جستجو با استفاده از UUID
        try:
            user_data = BaseUser.objects.get(id=request.user.id)
            # اگر کاربر پیدا شد، اطلاعات را به‌روزرسانی می‌کنیم
            user_data.first_name_fa = request.user.first_name_fa
            user_data.first_name_en = request.user.first_name_en
            user_data.last_name_fa = request.user.last_name_fa
            user_data.last_name_en = request.user.last_name_en
            user_data.usr_avatar = request.user.avatar_url
            user_data.is_superuser = request.user.is_superuser
            user_data.token = request.user.token
            user_data.save()
            message = "User data updated successfully."

            
        except BaseUser.DoesNotExist:
            # اگر کاربر وجود نداشت، یک شیء جدید ایجاد می‌کنیم
            user_data = BaseUser.objects.create(
                id=request.user.id,
                nationalcode=request.user.national_code,
                first_name_fa=request.user.first_name_fa,
                first_name_en=request.user.first_name_en,
                last_name_fa=request.user.last_name_fa,
                last_name_en=request.user.last_name_en,
                usr_avatar= request.user.avatar_url if request.user.avatar_url != "Null" else "",
                is_superuser=request.user.is_superuser,
                token=request.user.token
            )
            message = "User data created successfully."

        return JsonResponse({"message": message})
    else:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

@api_view(['GET'])
def group_chat_api(request, slug):
    # بررسی اینکه کاربر وارد شده باشد
    if not request.user.is_authenticated:
        return Response({"error": "برای مشاهده گروه‌ها باید وارد سیستم شوید."}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user  # کاربر فعلی
    userID = BaseUser.objects.get(id=request.user.id)
    # پیدا کردن گروه بر اساس slug
    group = get_object_or_404(Group, slug=slug)

    # دریافت پیام‌های گروه به ترتیب زمانی
    messages = Message.objects.filter(group=group).order_by('timestamp')

    # دریافت اعضای گروه
    members = group.members.all()

    # دریافت کاربران دیگری که عضو گروه نیستند
    all_users = BaseUser.objects.all()

    # تلاش برای پیدا کردن پروفایل کاربر وارد شده
    try:
        user_profile = UserProfile.objects.get(user=userID)
    except UserProfile.DoesNotExist:
        return Response({"error": "پروفایل کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

    # لیست اطلاعات اعضای گروه
    members_data = []
    for member in members:
        members_data.append({
            'id': member.id,
            'firstname': member.first_name_fa,
            'lastname': member.last_name_fa,
            'is_superuser': member.is_superuser,
            'avatar': member.usr_avatar,  # دریافت آواتار از فیلد usr_avatar در BaseUser
        })

    # لیست کاربران غیرعضو گروه
    all_users_data = [
        {
            'id': user.id,
            'firstname': user.first_name_fa,
            'lastname': user.last_name_fa,
            'avatar': user.usr_avatar  # دریافت آواتار از فیلد usr_avatar در BaseUser
        } 
        for user in all_users
    ]




     # آماده‌سازی پیام‌ها همراه با آواتار کاربران از BaseUser
    messages_data = []
    for message in messages:
        try:
            user = BaseUser.objects.get(id=message.user.id)
            avatar = user.usr_avatar if user.userprofile.avatar else None
        except UserProfile.DoesNotExist:
            avatar = None

        messages_data.append({
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp,
            'user_id': message.user.id,
            'user_name': message.user.first_name_fa + " " + message.user.last_name_fa,
            'avatar': avatar,
            'group': message.group.id,
            'file': message.file.url if message.file else None
        })

    # ساخت داده برای پاسخ
    data = {
        'group': {
            'id': group.id,
            'name': group.name,
            'slug': group.slug,
            'type': group.type,
            'members': members_data,
        },
        'messages':  messages_data,
        'all_users': all_users_data,
        'user_profile': UserProfileSerializer(user_profile).data,  # افزودن پروفایل کاربر وارد شده
    }

    return Response(data, status=status.HTTP_200_OK)



## Private Group
@api_view(['GET'])
def private_chat_api(request, slug):
    

    # بازیابی گروه خصوصی با توجه به نامک
    private_group = get_object_or_404(PrivateGroup, slug=slug)
    
    print(private_group)
    
    # بررسی اینکه آیا کاربر جزو اعضای گروه است یا نه
    if not (private_group.created_by == request.user or private_group.target_user == request.user or private_group.members.filter(id=request.user.id).exists()):
        return Response({"error": "You are not a member of this private chat group."}, status=status.HTTP_403_FORBIDDEN)
    
    # سریالایزر گروه خصوصی با پیام‌ها و اعضا
    private_group_data = PrivateGroupSerializer(private_group).data
    
    return Response({"private_group": private_group_data})


## Get All Users Data

@api_view(['GET'])
def all_users_with_groups_api(request):
    # دریافت تمام کاربران
    all_users = BaseUser.objects.all()
    
    # آماده‌سازی داده‌ها با اطلاعات گروه‌ها
    all_users_data = []
    for user in all_users:
        user_profile = UserProfile.objects.get(user=user)  # دریافت UserProfile مرتبط
        groups = user.group_members.all()  # دریافت گروه‌هایی که کاربر عضو آن‌هاست
        groups_data = [{'id': group.id, 'name': group.name, 'slug': group.slug, 'type': group.type} for group in groups]

        all_users_data.append({
            'profile_id': user_profile.id,
            'id': user.id,
            'firstname': user.first_name_fa,
            'lastname': user.last_name_fa,
            'avatar': user.usr_avatar,
            'is_superuser': user.is_superuser,
            'groups': groups_data  # لیست گروه‌ها
        })

    return Response({"all_users": all_users_data}, status=status.HTTP_200_OK)



## User Profile

class UserProfileAPIView(APIView):
    


    
    def get(self, request, *args, **kwargs):
        # بررسی اینکه کاربر وارد شده باشد
        if not request.user.is_authenticated:
            return Response({"error": "برای مشاهده پروفایل باید وارد سیستم شوید."}, status=status.HTTP_401_UNAUTHORIZED)

        # بررسی پارامتر get-all در درخواست
        get_all = request.query_params.get('get-all', None)

        if get_all and request.user.is_superuser:
            # اگر پارامتر get-all موجود باشد، تمام پروفایل‌ها را باز می‌گردانیم
            user_profiles = UserProfile.objects.all()
            message = "All User Profiles Retrieved"
            serializer = UserProfileSerializer(user_profiles, many=True)  # توجه: many=True برای لیست کردن تمام پروفایل‌ها
        else:
            user = request.user  # کاربر فعلی
            userID = BaseUser.objects.get(id=request.user.id)
            try:
                # تلاش برای پیدا کردن پروفایل کاربر
                user_profile = UserProfile.objects.get(user=userID)
                message = "User Profile Found"
            except UserProfile.DoesNotExist:
                # اگر پروفایل پیدا نشد، آن را ایجاد می‌کنیم
                user_profile = UserProfile.objects.create(
                    first_name=user.first_name_fa,
                    last_name=user.last_name_fa,
                    user=userID,
                    avatar=user.avatar_url
                )
                message = "New Profile Created"

            # سریالایزر پروفایل کاربر
            serializer = UserProfileSerializer(user_profile)

        return Response({
            "message": message,
            "data": serializer.data
        }, status=status.HTTP_200_OK)






class UserEmployeeView(APIView):
    def get(self, request, *args, **kwargs):
        bizid = request.query_params.get('bizid')
        roleid = request.query_params.get('roleid')
        token = request.headers.get('Authorization')

        # اطمینان از پر بودن پارامترهای ورودی
        if not bizid or not roleid or not token:
            return Response({"error": "پارامترهای لازم وارد نشده است"}, status=status.HTTP_400_BAD_REQUEST)

        # فراخوانی تابع `get_user_employees` به صورت همزمان
        employees_data = self.get_user_employees(bizid, roleid, token)

        if employees_data is None:
            return Response({"error": "خطا در دریافت اطلاعات از API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"data": employees_data}, status=status.HTTP_200_OK)

    def get_user_employees(self, bizid, roleid, token):
        try:
            cookies = {
                'token': token
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': token,
                'bizid': bizid,
                'roleid': roleid
            }

            # استفاده از httpx به صورت غیرهمزمان
            response = httpx.get(
                f"{API['user_employee_url']}",
                cookies=cookies,
                headers=headers
            )

            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                print(f'Error in receiving employees by API: status={response.status_code}')
                return []

        except httpx.RequestError as e:
            print(f'Error related to API: {str(e)}')
            return None
    


class PrivateChatView(APIView):
    def get(self, request, userid):
        if not request.user.is_authenticated:
            return Response(
                {"error": "برای مشاهده گروه‌ها باید وارد سیستم شوید."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user_uuid = UUID(userid)
            target_user = get_object_or_404(BaseUser, id=user_uuid)
        except (ValueError, TypeError):
            return Response({"error": "UUID معتبر نیست."}, status=status.HTTP_400_BAD_REQUEST)
        current_user_firstname = request.user.first_name_fa
        current_user_lastname = request.user.last_name_fa
        current_user_id = request.user.id  # گرفتن id کاربر فعلی
        target_user_id = target_user.id  # گرفتن id کاربر هدف

        # ساخت یک شناسه جدید با ترکیب id ها
        combined_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(current_user_id) + str(target_user_id))

        # تبدیل combined_uuid به رشته برای استفاده در private_chat_id
        private_chat_id = f"privatechat_{str(combined_uuid).replace('-', '')}"

        return Response({
            'private_chat_id': private_chat_id,
            'first_name': current_user_firstname,
            'last_name': current_user_lastname ,
            'target_user': {
                'userid': target_user.id,
                'first_name': target_user.first_name_fa,
                'last_name': target_user.last_name_fa,
            }
        }, status=status.HTTP_200_OK)



