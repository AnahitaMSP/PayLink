from django.contrib.auth import views as auth_views
from accounts.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .models import Profile
from .forms import ProfileUpdateForm
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from random import randint
from kavenegar import KavenegarAPI
from .forms import PhoneNumberForm, VerifyCodeForm, PasswordForm
import random
from kavenegar import KavenegarAPI, APIException, HTTPException
from django.contrib import messages
from .models import VerificationCode    
from django.contrib.auth.forms import SetPasswordForm
from .models import User
from datetime import timedelta
from django.utils import timezone


class LoginView(auth_views.LoginView):
    template_name='accounts/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True
   
class LogoutView(auth_views.LogoutView):
    pass

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        # اطمینان از اینکه کاربر فقط پروفایل خودش را ببیند
        return self.request.user.user_profile
    
API_KEY = '7450376C4463324C38356936654731333334466350633032493877513974333767725947776D49414F65383D'

def send_verification_code(receptor, token):
    try:
        api = KavenegarAPI(API_KEY)
        params = {
            'receptor': receptor,
            'template': 'your_template',  # قالب پیامک که از پنل کاوه نگار تنظیم شده است
            'token': token
        }
        response = api.verify_lookup(params)
        print(response)  # برای اشکال‌زدایی
    except APIException as e:
        print(f'API Exception: {e}')
    except HTTPException as e:
        print(f'HTTP Exception: {e}')

# مرحله اول: دریافت شماره تلفن
class RegistrationStepOneView(View):
    template_name = 'accounts/registration_step_1.html'
    form_class = PhoneNumberForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            if phone_number :
                print(phone_number)
            else: 
                print('no phone')
            
            # بررسی تکراری بودن شماره تلفن
            if User.objects.filter(phone_number=phone_number).exists():
                form.add_error('phone_number', 'شماره تلفن تکراری است. لطفاً شماره جدید وارد کنید.')
                return render(request, self.template_name, {'form': form})
            else:
                User.objects.get_or_create(phone_number=phone_number)

            verification_code = randint(100000, 999999)
            print(verification_code)

            send_verification_code(phone_number, verification_code)
            
            VerificationCode.objects.update_or_create(
                phone_number=phone_number,
                defaults={'code': verification_code}
            )

            messages.success(request, 'کد تایید به شماره شما ارسال شد.')
            request.session['phone_number'] = phone_number
            return redirect('accounts:registration_step_two')

        return render(request, self.template_name, {'form': form})
# مرحله دوم: تایید کد
class RegistrationStepTwoView(View):
    template_name = 'accounts/registration_step_2.html'
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # بررسی ارسال مجدد کد
        if 'resend_code' in request.POST:
            phone_number = request.session.get('phone_number')
            if phone_number:
                # تولید کد جدید
                new_verification_code = randint(100000, 999999)
                
                # ارسال کد جدید
                send_verification_code(phone_number, new_verification_code)
                
                # به‌روزرسانی کد در دیتابیس
                VerificationCode.objects.update_or_create(
                    phone_number=phone_number,
                    defaults={'code': new_verification_code}
                )
                
                messages.success(request, 'کد جدید ارسال شد.')
                return redirect('accounts:registration_step_two')
        
        # بررسی اعتبار کد وارد شده
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            phone_number = request.session.get('phone_number')

            try:
                verification = VerificationCode.objects.get(phone_number=phone_number)
                if verification.code == code:
                    messages.success(request, 'کد تایید معتبر است.')
                    return redirect('accounts:registration_step_three')
                else:
                    messages.error(request, 'کد نامعتبر یا منقضی شده است.')
            except VerificationCode.DoesNotExist:
                messages.error(request, 'شماره تلفن یافت نشد.')

        return render(request, self.template_name, {'form': form})

# مرحله سوم: انتخاب رمز عبور
class RegistrationStepThreeView(View):

    template_name = 'accounts/registration_step_3.html'

    def get(self, request):
        phone_number = request.session.get('phone_number')
        if not phone_number:
            # اگر شماره تلفن در نشست موجود نیست، کاربر را به مرحله اول هدایت کنید
            return redirect('accounts:registration_step_one')

        user = User.objects.get(phone_number=phone_number)
        form = PasswordForm(user=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        phone_number = request.session.get('phone_number')
        if not phone_number:
            # اگر شماره تلفن در نشست موجود نیست، کاربر را به مرحله اول هدایت کنید
            return redirect('accounts:registration_step_one')

        user = User.objects.get(phone_number=phone_number)
        form = PasswordForm(user=user, data=request.POST)

        if form.is_valid():
            form.save()
            user.is_verified = True
            user.save()
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
            return redirect('accounts:login')
        else:
            # چاپ خطاها برای اشکال‌زدایی
            print(form.errors)
            print('not valid form')

        # در صورتی که فرم نامعتبر باشد، صفحه فرم را با خطاها دوباره بارگذاری کنید
        return render(request, self.template_name, {'form': form})
    
class ForgotPasswordView(View):
    def get(self, request):
        phone_number_form = PhoneNumberForm()
        return render(request, 'accounts/forgot_password.html', {'phone_number_form': phone_number_form})

    def post(self, request):
        if 'send_code' in request.POST:
            phone_number_form = PhoneNumberForm(request.POST)
            if phone_number_form.is_valid():
                print('resetpass phone is valied')
                phone_number = phone_number_form.cleaned_data['phone_number']
                if not User.objects.filter(phone_number=phone_number).exists():
                    messages.error(request, 'شماره تلفن در سیستم موجود نیست. لطفاً ثبت نام کنید.')
                    return redirect('accounts:forgot_password')

                verification_code = randint(100000, 999999)
                send_verification_code(phone_number, verification_code)

                VerificationCode.objects.update_or_create(
                    phone_number=phone_number,
                    defaults={'code': verification_code}
                )

                messages.success(request, 'کد تایید به شماره شما ارسال شد.')
                request.session['phone_number'] = phone_number
                return redirect('accounts:verify_code')
            return render(request, 'accounts/forgot_password.html', {'phone_number_form': phone_number_form})

        elif 'verify_code' in request.POST:
            code_form = VerifyCodeForm(request.POST)
            if code_form.is_valid():
                code = code_form.cleaned_data['code']
                phone_number = request.session.get('phone_number')
                if not phone_number:
                    return redirect('accounts:forgot_password')

                try:
                    verification = VerificationCode.objects.get(phone_number=phone_number)
                    if verification.code == code and not verification.is_expired():
                        messages.success(request, 'کد تایید معتبر است.')
                        return redirect('accounts:set_password')
                    else:
                        messages.error(request, 'کد نامعتبر یا منقضی شده است.')
                except VerificationCode.DoesNotExist:
                    messages.error(request, 'شماره تلفن یافت نشد.')
                return redirect('accounts:verify_code')

        elif 'set_password' in request.POST:
            password_form = PasswordForm(user=User.objects.get(phone_number=request.session.get('phone_number')), data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'رمز عبور با موفقیت تغییر کرد.')
                return redirect('accounts:login')
            return render(request, 'accounts/set_password.html', {'password_form': password_form})

        return redirect('accounts:forgot_password')