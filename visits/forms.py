# visits/forms.py

from django import forms
from .models import Visit, PatientType
from accounts.models import Profile,Task

class VisitForm(forms.ModelForm):
    task = forms.ModelChoiceField(
        queryset=Task.objects.none(),  # تسک‌های مربوط به پروفایل پزشک را بارگذاری می‌کند
        widget=forms.Select(attrs={'class': 'form-control','placeholder': 'نوع خدمات'})
    )
    visit_fee = forms.DecimalField(
        max_digits=200, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'مبلغ ویزیت'}),
        required=False
    )
    patient_type = forms.ChoiceField(choices=PatientType.choices)

    class Meta:
        model = Visit
        fields = ['phone_number', 'patient_name', 'task', 'visit_fee', 'patient_type']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': '09xxxxxxxxx'}),
            'patient_name': forms.TextInput(attrs={'placeholder': 'نام بیمار'}),
            'patient_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'نوع بیمار'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # بارگذاری تسک‌های مربوط به پروفایل پزشک
        if user:
            user_profile = Profile.objects.get(user=user)
            self.fields['task'].queryset = Task.objects.filter(profile=user_profile)

        # به‌روزرسانی برچسب‌های فیلدها
        for field in self.fields:
            self.fields[field].label = ""

    def clean_task(self):
        task = self.cleaned_data.get('task')
        if task:
            return task
        return None

    def clean_visit_fee(self):
        task = self.cleaned_data.get('task')
        if task:
            return task.fee
        return None