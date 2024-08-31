from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import VisitForm
from django.views.generic import TemplateView
from payments.zibal import Zibal  # فرض بر این است که فایل zibal.py را ایجاد کرده‌اید
from payments.models import PaymentModel 

class CreateVisitView(LoginRequiredMixin, FormView):
    template_name = 'visits/create_visit.html'
    form_class = VisitForm
    success_url = reverse_lazy('visits:visit_success')
    
    def form_valid(self, form):
        visit = form.save(commit=False)
        visit.doctor = self.request.user
        visit.save()
        
        payment_url = self.create_payment_url(visit)
        if payment_url:
            return redirect(payment_url)
        else:
            # مدیریت وضعیت خطا
            form.add_error(None, "خطا در پردازش پرداخت. لطفاً دوباره تلاش کنید.")
            return self.form_invalid(form)
    
    def create_payment_url(self, visit):
        # هدایت به درگاه پرداخت
        zibal_instance = Zibal()
        response = zibal_instance.request(
            amount=visit.visit_fee,
            order_id=str(visit.id),  # برای تطابق با زیبال، بهتر است ID را به رشته تبدیل کنید
            mobile=visit.phone_number,  # فرض بر این است که شماره موبایل در پروفایل کاربر ذخیره شده است
            description="پرداخت هزینه بازدید"
        )
        
        if response.get('status') == 100:  # بررسی وضعیت موفقیت‌آمیز بودن درخواست
            payment_obj = PaymentModel.objects.create(
                authority_id=response.get("trackId"),  # توجه: زیبال از trackId به جای Authority استفاده می‌کند
                amount=visit.visit_fee
            )
            visit.payment = payment_obj
            visit.save()
            return response.get('url')  # زیبال ممکن است URL پرداخت را به عنوان 'url' برگرداند
        else:
            # مدیریت خطاها
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.user_profile
        context['full_name'] = user_profile.get_fullname()

        return context

class VisitSuccessView(TemplateView):
    template_name = 'visits/visit_success.html'
