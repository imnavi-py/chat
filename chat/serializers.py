# # serializers.py
# from rest_framework import serializers
# from django.contrib.auth.models import User

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password', 'email']  # فیلدهای مورد نیاز
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = User(**validated_data)
#         user.set_password(validated_data['password'])  # هش کردن رمز عبور
#         user.save()
#         return user




from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import BaseUser, Group, PrivateGroup, PrivateMessage
from .utils import convert_to_ascii  # فرض کنید این تابع برای تبدیل به ASCII است
from rest_framework import serializers
from .models import Group, Message, UserProfile
from django.contrib.auth.models import User  # Import User model

class CreateGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
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
        group = Group.objects.create(name=group_name, slug=convert_to_ascii(slug), created_by=request.user, type=group_type)
        group.members.add(request.user)

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



class MessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name_fa', read_only=True)
    avatar = serializers.ImageField(source='user.userprofile.avatar', read_only=True)
    
    # اصلاح فیلد 'user' برای تبدیل شناسه به شیء BaseUser
    user = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all(), required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'user', 'user_name', 'avatar', 'group', 'file']



class UserProfileSerializer(serializers.ModelSerializer):
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    # username = serializers.CharField(source='user.username', read_only=True)  # اضافه کردن فیلد نام کاربری

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'avatar', 'is_superuser']

class MemberSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)


    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'is_superuser']  # فیلدهای مورد نیاز

class GroupSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'slug', 'type', 'members']# حذف members_names چون اطلاعاتش در MemberSerializer است

class GroupChatSerializer(serializers.Serializer):
    group = GroupSerializer()  # استفاده از GroupSerializer به جای group = Group
    messages = MessageSerializer(many=True)
    all_users = serializers.PrimaryKeyRelatedField(many=True, queryset=BaseUser.objects.all())
    user_profile = UserProfileSerializer()

    def get_all_users_names(self, obj):
        return [user.username for user in obj.all_users]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # اصلاح: از داده‌های instance برای دریافت اطلاعات group استفاده کنید
        group = instance.get('group')  # گروه به درستی به این فیلد اختصاص داده شده باشد

        if group:
            messages = Message.objects.filter(group=group).order_by('timestamp')
            representation['messages'] = MessageSerializer(messages, many=True).data
            representation['members'] = [MemberSerializer(member).data for member in group.members.all()]
        
        return representation
    
## Private Group

class PrivateMessageSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.SerializerMethodField()
    sender_avatar = serializers.CharField(source='sender.userprofile.avatar', read_only=True)
    recipient_full_name = serializers.SerializerMethodField()
    recipient_avatar = serializers.CharField(source='recipient.userprofile.avatar', read_only=True)

    # اصلاح فیلدهای sender و recipient برای تبدیل شناسه به شیء BaseUser
    sender = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all(), required=True)
    recipient = serializers.PrimaryKeyRelatedField(queryset=BaseUser.objects.all(), required=True)
    pvgroup = serializers.PrimaryKeyRelatedField(queryset=PrivateGroup.objects.all(), required=True)

    class Meta:
        model = PrivateMessage
        fields = ['id', 'content', 'timestamp', 'sender', 'sender_full_name', 'sender_avatar', 
                  'recipient', 'recipient_full_name', 'recipient_avatar', 'file', 'pvgroup']
    def get_sender_full_name(self, obj):
        return f"{obj.sender.first_name_fa} {obj.sender.last_name_fa}"

    def get_recipient_full_name(self, obj):
        return f"{obj.recipient.first_name_fa} {obj.recipient.last_name_fa}"

class PrivateGroupMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(source='avatar', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'avatar']



class PrivateGroupSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    # sender = serializers.SerializerMethodField()
    # recipient = serializers.SerializerMethodField()
    private_with = serializers.SerializerMethodField()
    # priv_with =  

    class Meta:
        model = PrivateGroup
        fields = ['id', 'name', 'slug', 'members', 'messages', 'private_with']

    def get_messages(self, obj):
        messages = PrivateMessage.objects.filter(pvgroup=obj).order_by('timestamp')
        return PrivateMessageSerializer(messages, many=True).data

    def get_private_with(self, obj):
        # گیرنده به صورت `target_user` ذخیره شده است
        priv_with = ""
        recipient = obj.target_user
        sender = obj.created_by
        recipient = obj.target_user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            print("this is :", request.user.id)
            if sender.id == request.user.id:
                priv_with = recipient
            else:
                priv_with = sender
            
        print("no")
        return {

            "id": priv_with.id,
            "full_name": f"{priv_with.first_name_fa} {priv_with.last_name_fa}",
            "avatar": priv_with.usr_avatar,  # اگر avatar در BaseUser ذخیره شده است
        }