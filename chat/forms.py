# from django import forms
# from django.contrib.auth.models import User
# from .models import Group, UserProfile

# from django import forms

# from django import forms

# class UserLoginForm(forms.Form):
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'نام کاربری'
#         }),
#         label="نام کاربری"
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'رمز عبور'
#         }),
#         label="رمز عبور"
#     )



# class UserRegistrationForm(forms.Form):
    
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'نام کاربری'
#         }),
#         label="نام کاربری"
#     )
#     email = forms.EmailField(  # استفاده از EmailField
#         widget=forms.EmailInput(attrs={  # تغییر به EmailInput
#             'class': 'form-control',
#             'placeholder': 'ایمیل'
#         }),
#         label="ایمیل"
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'رمز عبور'
#         }),
#         label="رمز عبور"
#     )

#     def save(self):
#         # یک کاربر جدید ایجاد کنید و اطلاعات را ذخیره کنید
#         user = User(
#             username=self.cleaned_data['username'],
#             email=self.cleaned_data['email']
#         )
#         user.set_password(self.cleaned_data['password'])
#         user.save()
#         return user

    

    

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['first_name', 'last_name', 'avatar']


# class GroupSearchForm(forms.Form):
#     search_term = forms.CharField(label='جستجوی گروه', max_length=100)


# class GroupForm(forms.ModelForm):
#     class Meta:
#         model = Group
#         fields = ['name', 'slug', 'type']  # نام، نامک و نوع گروه
#         widgets = {
#             'slug': forms.TextInput(attrs={'placeholder': 'Slug (only in English characters)'}),
#         }