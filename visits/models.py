# visits/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone

class Visit(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # تغییر به settings.AUTH_USER_MODEL
    phone_number = models.CharField(max_length=12)
    patient_name = models.CharField(max_length=255)
    visit_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_link = models.URLField(max_length=200, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    payment = models.ForeignKey('payments.PaymentModel',on_delete=models.SET_NULL,null=True  )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_name} - {self.phone_number}"
