from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError
from .models import Profile,Province,City
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
        fields = [
            'first_name', 'last_name', 'image', 'job', 'national_code', 'iban',
            'bank_card_number', 'province', 'city', 'address', 'tell_phone', 'gender',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'tell_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'province': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
        }

    job = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        required=False,
        empty_label="انتخاب شغل",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        required=False,
        empty_label="انتخاب استان",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        empty_label="انتخاب شهر",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    gender = forms.ChoiceField(
        choices=[('male', 'مرد'), ('female', 'زن'), ('other', 'سایر')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.type != UserType.provider.value:
            self.fields.pop('job')  # حذف فیلد شغل در صورتی که نوع کاربر provider نباشد


class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=12,
        validators=[RegexValidator(regex=r'^[0-9]{11}$', message='شماره تلفن باید 11 رقم باشد')]
    )

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

