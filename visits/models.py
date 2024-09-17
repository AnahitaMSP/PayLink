# visits/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import Task


class PatientType(models.TextChoices):
    INDIVIDUAL = 'individual', _('شخص')
    COMPANY = 'company', _('شرکت')
    CLINIC = 'clinic', _('کلینیک')
    LABORATORY = 'laboratory', _('آزمایشگاه')

class Visit(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visits')
    phone_number = models.CharField(max_length=15)
    patient_name = models.CharField(max_length=255)
    patient_type = models.CharField(max_length=20, choices=PatientType.choices, default=PatientType.INDIVIDUAL)
    visit_fee = models.DecimalField(max_digits=200, decimal_places=2)
    payment_link = models.URLField(max_length=200, blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='visits')  # Add this field
    is_paid = models.BooleanField(default=False)
    payment = models.ForeignKey('payments.PaymentModel', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.patient_name} - {self.phone_number}"


class Invoice(models.Model):
    visit = models.OneToOneField('visits.Visit', on_delete=models.CASCADE)  # هر فاکتور مربوط به یک ویزیت است
    invoice_number = models.CharField(max_length=255, unique=True)  # شماره فاکتور
    issue_date = models.DateTimeField(default=timezone.now)  # تاریخ صدور فاکتور
    due_date = models.DateTimeField(null=True, blank=True)  # تاریخ سررسید فاکتور (اختیاری)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # مبلغ فاکتور
    is_paid = models.BooleanField(default=False)  # وضعیت پرداخت
    payment_link = models.URLField(max_length=500, blank=True, null=True)  

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.visit.patient_name}"
    
