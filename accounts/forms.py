from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError
from .models import Profile,Province,City
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from .models import User
from django.core.validators import RegexValidator
from .models import Profile, Task,UserType,ServiceType, Specialty


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
            'specialties'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'نام خانوادگی'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control','placeholder':'کد ملی'}),
            'iban': forms.TextInput(attrs={'class': 'form-control','placeholder':'شماره شبا'}),
            'bank_card_number': forms.TextInput(attrs={'class': 'form-control','placeholder':'شماره کارت'}),
            'address': forms.TextInput(attrs={'class': 'form-control','placeholder':'آدرس'}),
            'tell_phone': forms.TextInput(attrs={'class': 'form-control','placeholder':'تلفن ثابت'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'province': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'specialties': forms.SelectMultiple(attrs={'class': 'form-control', 'placeholder': 'تخصص'}),  
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
    specialties = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        widget=forms.Select
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.type != UserType.provider.value:
            self.fields.pop('job')  # حذف فیلد شغل در صورتی که نوع کاربر provider نباشد


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'fee']  # نام وظیفه و قیمت
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':"نوع خدمت"}),
            'fee': forms.TextInput(attrs={'class': 'form-control','placeholder':'مبلغ به ریال'}),

        }  

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=12,
        label="شماره تلفن همراه خود را وارد کنید.",
        validators=[RegexValidator(regex=r'^[0-9]{11}$', message='شماره موبایل درست نیست. لطفاً یک شماره معتبر وارد کنید.')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Adding Bootstrap form-control class
            'placeholder': '09xxxxxxxxx',
            'required': 'required',
        })
    )
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        # بررسی وجود شماره موبایل در دیتابیس
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('شماره موبایل تکراری است. لطفا از بخش ورود وارد پروفایل خود شوید.')

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

