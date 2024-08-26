from django import forms
from .models import Visit

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['phone_number', 'patient_name', 'visit_fee']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': '09xxxxxxxxx'}),
            'patient_name': forms.TextInput(attrs={'placeholder': 'نام بیمار'}),
            'visit_fee': forms.NumberInput(attrs={'placeholder': 'مبلغ ویزیت'}),
        }