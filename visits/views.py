from django.shortcuts import  redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import VisitForm
from django.views.generic import TemplateView
from payments.zarinpal_client import ZarinPalSandbox
from payments.models import PaymentModel 

class CreateVisitView(LoginRequiredMixin, FormView):
    template_name = 'visits/create_visit.html'
    form_class = VisitForm
    success_url = reverse_lazy('visits:visit_success')

    def form_valid(self, form):
        visit = form.save(commit=False)
        visit.doctor = self.request.user
        visit.save()
        
        return redirect(self.create_payment_url(visit))
    def create_payment_url(self,visit):
        # هدایت به درگاه پرداخت\
        zarinpal = ZarinPalSandbox()
        response = zarinpal.payment_request(visit.visit_fee)
        
        payment_obj=PaymentModel.objects.create(
            authority_id = response.get("Authority"),
            amount = visit.visit_fee
        )
        visit.payment = payment_obj
        visit.save()
        return zarinpal.generate_payment_url(response.get('Authority')) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.user_profile
        context['full_name'] = user_profile.get_fullname()

        return context

    
class VisitSuccessView(TemplateView):
    template_name = 'visits/visit_success.html'