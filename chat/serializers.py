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
from .models import Group
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
    user_name = serializers.ReadOnlyField(source='user.username')
    avatar = serializers.ImageField(source='user.userprofile.avatar', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'user', 'user_name', 'avatar', 'file']

class UserProfileSerializer(serializers.ModelSerializer):
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)  # اضافه کردن فیلد نام کاربری

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'avatar', 'is_superuser', 'username']

class MemberSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    print("super usere ?" ,is_superuser)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'is_superuser']  # فیلدهای مورد نیاز

class GroupSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)  # استفاده از MemberSerializer

    class Meta:
        model = Group
        fields = ['id', 'name', 'slug', 'type', 'members']  # حذف members_names چون اطلاعاتش در MemberSerializer است

class GroupChatSerializer(serializers.Serializer):
    group = GroupSerializer()
    messages = MessageSerializer(many=True)
    all_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    user_profile = UserProfileSerializer()

    def get_all_users_names(self, obj):
        return [user.username for user in obj.all_users]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['members'] = [MemberSerializer(member).data for member in instance.members.all()]
        return representation