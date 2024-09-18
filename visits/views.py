from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.conf import settings
import requests

from visits.models import PatientType, Visit, Invoice
from .forms import VisitForm
from payments.models import PaymentModel, PaymentStatusType
from accounts.models import Profile


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  
        return kwargs

    def form_valid(self, form):
        visit = form.save(commit=False)
        visit.doctor = self.request.user

        task = form.cleaned_data.get('task')
        if task:
            visit.visit_fee = task.fee

        visit.save()

        payment_url = self.create_payment_url(visit)
        if payment_url:
            invoice = self.create_invoice(visit, payment_url)
            if invoice:
                self.send_invoice_sms(visit.phone_number, invoice)
                return render(self.request, 'visits/invoice_sent.html', {
                    'phone_number': visit.phone_number,
                    'invoice_number': invoice.invoice_number
                })
            else:
                form.add_error(None, "خطا در ایجاد فاکتور. لطفاً دوباره تلاش کنید.")
                return self.form_invalid(form)
        else:
            form.add_error(None, "خطا در ایجاد لینک پرداخت. لطفاً دوباره تلاش کنید.")
            return self.form_invalid(form)

    def create_payment_url(self, visit):
        """
        ایجاد لینک پرداخت از طریق API نوین‌پال
        """
        payment_data = {
            "api_key": settings.NOVINPAL_API_KEY,
            "amount": int(visit.visit_fee * 10),  
            "return_url": settings.NOVINPAL_RETURN_URL,
            "order_id": f"VISIT-{visit.id}",
            "description": f"پرداخت ویزیت برای {visit.patient_name}",
            "mobile": visit.phone_number
        }
        response = requests.post(settings.NOVINPAL_REQUEST_URL, json=payment_data)
        response_data = response.json()

        if response_data.get('status') == 1:
            payment = PaymentModel.objects.create(
                authority_id=response_data['refId'],
                amount=visit.visit_fee,
                status=PaymentStatusType.pending
            )
            visit.payment = payment
            visit.save()

            return f"{settings.NOVINPAL_START_URL}{response_data['refId']}"
        else:
            return None

    def create_invoice(self, visit, payment_url):
        """
        ایجاد فاکتور جدید برای ویزیت
        """
        invoice_number = f"DRDX-{visit.id}-{visit.created_at.strftime('%Y%m%d%H%M%S')}"
        invoice = Invoice.objects.create(
            visit=visit,
            invoice_number=invoice_number,
            amount=visit.visit_fee,
            payment_link=payment_url  
        )
        return invoice

    def send_invoice_sms(self, phone_number, invoice):
        """
        ارسال پیامک حاوی لینک فاکتور و لینک پرداخت به بیمار
        """
        invoice_url = f"http://panel.doctordex.ir/visits/invoices/{invoice.invoice_number}/"
        api_key = settings.KAVENEGAR_API_KEY  # استفاده از کلید API واقعی
        template = "send-payment-link"  # نام الگوی پیامک تعریف شده در پنل کاوه‌نگار
        send_paymentlink_sms(api_key, phone_number, invoice_url, template)


class InvoiceDetailView(View):
    def get(self, request, invoice_number, *args, **kwargs):
        try:
            invoice = Invoice.objects.get(invoice_number=invoice_number)
            return render(request, 'visits/invoice_detail.html', {'invoice': invoice})
        except Invoice.DoesNotExist:
            return HttpResponse("فاکتور پیدا نشد.", status=404)


class CreatePaymentLinkView(View):
    def post(self, request, invoice_number, *args, **kwargs):
        invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
        visit = invoice.visit
        
        payment_url = self.create_payment_url(visit)
        
        if payment_url:
            invoice.payment_link = payment_url
            invoice.save()

            self.send_invoice_sms(visit.phone_number, invoice)
            
            return redirect('visits:invoice_detail', invoice_number=invoice_number)
        else:
            return HttpResponse("خطا در ایجاد لینک پرداخت. لطفاً دوباره تلاش کنید.", status=500)

    def create_payment_url(self, visit):
        """
        ایجاد لینک پرداخت از طریق API نوین‌پال
        """
        payment_data = {
            "api_key": settings.NOVINPAL_API_KEY,
            "amount": int(visit.visit_fee * 10),  
            "return_url": settings.NOVINPAL_RETURN_URL,
            "order_id": f"VISIT-{visit.id}",
            "description": f"پرداخت ویزیت برای {visit.patient_name}",
            "mobile": visit.phone_number
        }
        response = requests.post(settings.NOVINPAL_REQUEST_URL, json=payment_data)
        response_data = response.json()

        if response_data.get('status') == 1:
            payment = PaymentModel.objects.create(
                authority_id=response_data['refId'],
                amount=visit.visit_fee,
                status=PaymentStatusType.pending
            )
            visit.payment = payment
            visit.save()

            return f"{settings.NOVINPAL_START_URL}{response_data['refId']}"
        else:
            return None

    def send_invoice_sms(self, phone_number, invoice):
        """
        ارسال پیامک حاوی لینک فاکتور و لینک پرداخت به بیمار
        """
        # لینک فاکتور
        invoice_url = f"http://panel.doctordex.ir/visits/invoices/{invoice.invoice_number}/"
        api_key = settings.KAVENEGAR_API_KEY 
        template = "send-payment-link"  
        # ارسال پیامک
        send_paymentlink_sms(api_key, phone_number, invoice_url, template)


class PaymentListView(ListView):
    model = Visit
    template_name = 'visits/payment_report.html'
    context_object_name = 'visits'

    def get_queryset(self):
        doctor = self.request.user
        
        status = self.kwargs.get('status')
        
        return Visit.objects.filter(doctor=doctor, payment__status=status).select_related('payment', 'task')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.kwargs.get('status')

        if status == 1:
            context['title'] = 'پرداخت‌های در انتظار'
        elif status == 2: 
            context['title'] = 'پرداخت‌های موفق'
        elif status == 3:
            context['title'] = 'پرداخت‌های ناموفق'

        for visit in context['visits']:
            visit.patient_type_display = dict(PatientType.choices).get(visit.patient_type)
            visit.task_name = visit.task.name if visit.task else "بدون وظیفه"

        return context