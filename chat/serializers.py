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
