from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from visits.models import Visit
from .forms import VisitForm
from payments.models import PaymentModel, PaymentStatusType
from django.http import HttpResponse
import requests
from django.conf import settings


def send_paymentlink_sms(api_key, receptor, token, template, message_type='sms'):
    url = f'https://api.kavenegar.com/v1/{api_key}/verify/lookup.json'
    params = {
        'receptor': receptor,
        'token': token,
        'template': template,
        'type': message_type
    }
    response = requests.get(url, params=params)
    return response.json()


class CreateVisitView(LoginRequiredMixin, FormView):
    template_name = 'visits/create_visit.html'
    form_class = VisitForm

    def form_valid(self, form):
        visit = form.save(commit=False)
        visit.doctor = self.request.user
        visit.save()

        payment_url = self.create_payment_url(visit)
        if payment_url:
            # ارسال پیامک حاوی لینک پرداخت
            self.send_payment_sms(visit.phone_number, payment_url)
            # ارسال پیغام به قالب
            return render(self.request, 'visits/payment_link_sent.html', {
                'phone_number': visit.phone_number
            })
        else:
            form.add_error(None, "خطا در پردازش پرداخت. لطفاً دوباره تلاش کنید.")
            return self.form_invalid(form)

    def create_payment_url(self, visit):
        # ساختن درخواست به API نوین‌پال برای ایجاد تراکنش
        payment_data = {
            "api_key": settings.NOVINPAL_API_KEY,
            "amount": int(visit.visit_fee * 10),  # مبلغ به ریال
            "return_url": settings.NOVINPAL_RETURN_URL,
            "order_id": f"VISIT-{visit.id}",
            "description": f"پرداخت ویزیت برای {visit.patient_name}",
            "mobile": visit.phone_number
        }
        response = requests.post(settings.NOVINPAL_REQUEST_URL, json=payment_data)
        response_data = response.json()

        if response_data.get('status') == 1:
            # ثبت اطلاعات پرداخت در دیتابیس
            payment = PaymentModel.objects.create(
                authority_id=response_data['refId'],
                amount=visit.visit_fee,
                status=PaymentStatusType.pending
            )
            visit.payment = payment
            visit.save()

            # بازگرداندن URL پرداخت
            return f"{settings.NOVINPAL_START_URL}{response_data['refId']}"
        else:
            return None

    def send_payment_sms(self, phone_number, payment_url):
        """
        ارسال پیامک حاوی لینک پرداخت به کاربر
        """
        api_key = '6E746B36304649736E304177367A307175776575365A6D772B716858755833494D634553355066755445513D'
        template = "send-payment-link"  # نام الگوی پیامک تعریف‌شده در پنل کاوه‌نگار
        send_paymentlink_sms(api_key, phone_number, payment_url, template)

class VerifyPaymentView(View):
    def get(self, request, *args, **kwargs):
        ref_id = request.GET.get('refId')
        success = request.GET.get('success')

        # بررسی موفقیت تراکنش
        if success == '1':
            payment = PaymentModel.objects.get(authority_id=ref_id)

            # ارسال درخواست تأیید به نوین‌پال
            verify_data = {
                "api_key": settings.NOVINPAL_API_KEY,
                "ref_id": ref_id
            }
            response = requests.post(settings.NOVINPAL_VERIFY_URL, json=verify_data)
            response_data = response.json()

            if response_data.get('status') == 1:
                # تراکنش موفق
                payment.status = PaymentStatusType.success
                payment.ref_id = response_data['refNumber']
                payment.save()

                visit = Visit.objects.get(payment=payment)
                visit.is_paid = True
                visit.save()

                return render(request, 'visits/payment_success.html', {
                    'message': "پرداخت موفقیت‌آمیز بود."
                })
            else:
                # تراکنش ناموفق
                payment.status = PaymentStatusType.failed
                payment.save()
                return render(request, 'visits/payment_failed.html', {
                    'message': "پرداخت ناموفق بود."
                })

        # در صورت عدم موفقیت در پرداخت یا تایید، به صفحه خطا بروید
        return render(request, 'visits/payment_failed.html', {
            'message': "پرداخت ناموفق بود."
        })