from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError
from .models import Profile
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from .models import User
from django.core.validators import RegexValidator
from .models import Profile ,UserType,ServiceType


class AuthenticationForm(auth_forms.AuthenticationForm):
    def confirm_login_allowed(self, user):
        super(AuthenticationForm, self).confirm_login_allowed(user)

        if not user.is_verified:  # فرض بر این است که اگر کاربر تأیید نشده باشد خطا صادر شود
            raise ValidationError(
                'حساب کاربری شما هنوز تأیید نشده است.',  # پیام مناسب برای کاربر
                code='unverified'
            )

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image', 'job']  # شامل فیلد شغل

    job = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        required=False,
        empty_label="انتخاب شغل"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.type != UserType.provider.value:
            self.fields.pop('job')  # 

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=12,
        validators=[RegexValidator(regex=r'^[0-9]{11}$', message='شماره تلفن باید 11 رقم باشد')]
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('شماره تلفن تکراری است. لطفاً شماره جدید وارد کنید.')
        return phone_number
# فرم تایید کد در مرحله دوم
class VerifyCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'کد تایید را وارد کنید'})
    )

class PasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = "رمز عبور جدید"
        self.fields['new_password2'].label = "تکرار رمز عبور جدید"

