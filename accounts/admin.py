from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile ,ServiceType
from django.contrib.auth import get_user_model
from .models import VerificationCode
from django.contrib.sessions.models import Session

User = get_user_model()

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at')
    search_fields = ('phone_number',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)  # فیلدهایی که فقط برای خواندن هستند

    def is_code_valid(self, obj):
        return obj.is_code_valid()

class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for user management with add and change forms plus password
    """

    model = User
    list_display = ("id", "phone_number", "type", "is_superuser", "is_active", "is_verified")
    list_filter = ("type", "is_superuser", "is_active", "is_verified")
    searching_fields = ("phone_number", "email")
    ordering = ("phone_number",)

    fieldsets = (
        (
            "Authentication",
            {
                "fields": ("phone_number", "email", "password"),
            },
        ),
        (
            "permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                ),
            },
        ),
        (
            "group permissions",
            {
                "fields": ("groups", "user_permissions", "type"),
            },
        ),
        (
            "important date",
            {
                "fields": ("last_login",),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "type",
                ),
            },
        ),
    )


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name")
    list_filter = ("user__type",)  # فیلتر بر اساس نوع کاربر (User Type)
    search_fields = ("first_name", "last_name", "user__phone_number")


admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(VerificationCode, VerificationCodeAdmin)

admin.site.register(ServiceType, ServiceTypeAdmin)


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']


admin.site.register(Session, SessionAdmin)
