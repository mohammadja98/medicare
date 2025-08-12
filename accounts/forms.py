# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    # افزودن فیلد is_doctor به صورت Checkbox
    is_doctor = forms.BooleanField(label="Are you a doctor?", required=False)

    class Meta:
        model = get_user_model()
        # فیلدهایی که در فرم ثبت نام نمایش داده می‌شوند
        fields = ('email', 'username', 'is_doctor',)

    # متد signup که توسط allauth نیاز است
    def signup(self, request, user):
        # مقدار is_doctor را از فرم گرفته و در مدل کاربر ذخیره می‌کند
        user.is_doctor = self.cleaned_data['is_doctor']
        user.save()

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'is_doctor',)

