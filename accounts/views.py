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
import requests
from django.http import JsonResponse
from .models import City
from .models import Profile, Specialty
from django.views.generic.edit import UpdateView
from django.core.exceptions import PermissionDenied

from django.views.generic.edit import CreateView
from .models import Task
from .forms import TaskForm

from django.shortcuts import render, get_object_or_404

def load_cities(request):
    province_id = request.GET.get('province_id')
    cities = City.objects.filter(province_id=province_id).all()
    return JsonResponse(list(cities.values('id', 'name')), safe=False)

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

    def form_valid(self, form):
        # اگر فرم معتبر باشد، پیام موفقیت اضافه کنید
        messages.success(self.request, 'پروفایل با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        # چاپ خطاها در صورت نامعتبر بودن فرم
        print(form.errors)  # چاپ خطاها در کنسول
        for field in form:
            print(f"Errors in {field.name}: {field.errors}")

        return super().form_invalid(form)
    

def send_verification_sms(api_key, receptor, token, template, message_type='sms'):

    url = f'https://api.kavenegar.com/v1/{api_key}/verify/lookup.json'
    params = {
        'receptor': receptor,
        'token': token,
        'template': template,
        'type': message_type
    }
    
    response = requests.get(url, params=params)
    return response.json()

class ProfileTaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'accounts/add_task.html'
    success_url = reverse_lazy('accounts:add_task')

    def form_valid(self, form):
        form.instance.profile = self.request.user.user_profile  # اتصال وظیفه به پروفایل پزشک
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # دریافت لیست وظایف مربوط به پروفایل کاربر جاری
        context['tasks'] = Task.objects.filter(profile=self.request.user.user_profile)
        return context
    
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

            # کلید API و الگوی پیامک را اینجا تنظیم کنید
            api_key = '61484C346A6933724834676C4C6E4F6B7A4D666D646C5A676A422F6A2B63467263456B324753354F4F62593D'
            template = 'send-register-code'
            
            # ارسال کد تایید
            send_verification_sms(api_key, phone_number, verification_code, template)            
            VerificationCode.objects.update_or_create(
                phone_number=phone_number,
                defaults={'code': verification_code}
            )

            messages.success(request, 'کد تایید به شماره شما ارسال شد.')
            request.session['phone_number'] = phone_number
            return redirect('accounts:registration_step_two')

        return render(request, self.template_name, {'form': form})
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
                print(new_verification_code)

                # کلید API و الگوی پیامک را اینجا تنظیم کنید
                api_key = '6E746B36304649736E304177367A307175776575365A6D772B716858755833494D634553355066755445513D'
                template = 'send-register-code'
                
                # ارسال کد تایید
                send_verification_sms(api_key, phone_number, new_verification_code, template)   
                
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
    template_name = 'accounts/forgot_password.html'
    form_class = PhoneNumberForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                form.add_error('phone_number', 'این شماره تلفن ثبت نشده است.')
                return render(request, self.template_name, {'form': form})

            # Generate a new verification code
            verification_code = randint(100000, 999999)
            print(verification_code)

            # کلید API و الگوی پیامک را اینجا تنظیم کنید
            api_key = '6E746B36304649736E304177367A307175776575365A6D772B716858755833494D634553355066755445513D'
            template = 'send-register-code'
            
            # ارسال کد تایید
            send_verification_sms(api_key, phone_number, verification_code, template)
            # Send the verification code via SMS

            # Save or update the verification code in the database
            VerificationCode.objects.update_or_create(
                phone_number=phone_number,
                defaults={'code': verification_code}
            )

            # Inform the user that the code has been sent
            messages.success(request, 'کد تایید به شماره شما ارسال شد.')
            request.session['phone_number'] = phone_number
            return redirect('accounts:verify_code')

        return render(request, self.template_name, {'form': form})
    
class VerifyCodeView(View):
    template_name = 'accounts/verify_code.html'
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            phone_number = request.session.get('phone_number')

            if not phone_number:
                return redirect('accounts:forgot_password')

            try:
                verification = VerificationCode.objects.get(phone_number=phone_number)
                if verification.code == code:
                    messages.success(request, 'کد تایید معتبر است.')
                    return redirect('accounts:reset_password')
                else:
                    messages.error(request, 'کد نامعتبر یا منقضی شده است.')
            except VerificationCode.DoesNotExist:
                messages.error(request, 'شماره تلفن یافت نشد.')

        return render(request, self.template_name, {'form': form})
    
class ResetPasswordView(View):
    template_name = 'accounts/set_password.html'

    def get(self, request):
        phone_number = request.session.get('phone_number')
        if not phone_number:
            return redirect('accounts:forgot_password')

        user = User.objects.get(phone_number=phone_number)
        form = SetPasswordForm(user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        phone_number = request.session.get('phone_number')
        if not phone_number:
            return redirect('accounts:forgot_password')

        user = User.objects.get(phone_number=phone_number)
        form = SetPasswordForm(user, request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت.')
            return redirect('accounts:password_change_success')
        else:
            messages.error(request, 'لطفاً فرم را با دقت تکمیل کنید.')

        return render(request, self.template_name, {'form': form})
    
class PasswordChangeSuccessView(View):
    template_name = 'accounts/password_change_success.html'

    def get(self, request):
        return render(request, self.template_name)