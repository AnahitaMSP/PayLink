from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from visits.models import Visit
from .forms import VisitForm
from accounts.models import Profile
from django.views.generic import TemplateView

import logging
from django.urls import reverse
from azbankgateways import (
    bankfactories,
    models as bank_models,
    default_settings as settings,
)
from azbankgateways.exceptions import AZBankGatewaysException
import logging

from django.http import HttpResponse, Http404
from django.urls import reverse

from azbankgateways import (
    bankfactories,
    models as bank_models,
    default_settings as settings,
)

class CreateVisitView(LoginRequiredMixin, FormView):
    template_name = 'visits/create_visit.html'
    form_class = VisitForm
    success_url = reverse_lazy('visits:visit_success')

    def form_valid(self, form):
        visit = form.save(commit=False)
        visit.doctor = self.request.user
        visit.save()

        # هدایت به درگاه پرداخت
        return redirect('visits:go_to_gateway', visit_id=visit.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.user_profile
        context['full_name'] = user_profile.get_fullname()
        return context

def go_to_gateway_view(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    amount = visit.visit_fee  # مبلغ ویزیت
    user_mobile_number = visit.phone_number  # شماره موبایل کاربر

    factory = bankfactories.BankFactory()
    try:
        bank = factory.auto_create()
        bank.set_request(request)
        bank.set_amount(amount)
        bank.set_client_callback_url(reverse("visits:callback_gateway"))

        bank.set_mobile_number(user_mobile_number)

        bank_record = bank.ready()

        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        return HttpResponse("خطا در اتصال به درگاه پرداخت. لطفا دوباره تلاش کنید.")

def callback_gateway_view(request):


    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        raise Http404

    if bank_record.is_success:
        return HttpResponse("پرداخت با موفقیت انجام شد.")
    else:
        return HttpResponse("پرداخت با شکست مواجه شد. اگر پول کم شده است ظرف مدت ۴۸ ساعت به حساب شما بازخواهد گشت.")
    
class VisitSuccessView(TemplateView):
    template_name = 'visits/visit_success.html'