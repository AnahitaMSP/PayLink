# visits/admin.py

from django.contrib import admin
from .models import Visit

class VisitAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'phone_number', 'patient_name', 'visit_fee', 'is_paid','patient_type' , 'created_at')
    list_filter = ('doctor', 'is_paid', 'created_at')
    search_fields = ('phone_number', 'patient_name')
    ordering = ('-created_at',)

admin.site.register(Visit, VisitAdmin)
