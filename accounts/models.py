from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from accounts.validators import validate_iranian_cellphone_number
from django.utils import timezone
import datetime


class ServiceType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class UserType(models.IntegerChoices):
    customer = 1, _("customer")
    admin = 2, _("admin")
    superuser = 3, _("superuser")
    provider = 4, _("provider")


class UserManager(BaseUserManager):
    """
    Custom user model manager where phone number is the unique identifier
    for authentication instead of usernames.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and save a User with the given phone number and password.
        """
        if not phone_number:
            raise ValueError(_("The Phone number must be set"))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)  # اضافه کردن using برای سازگاری
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given phone number and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("type", UserType.superuser.value)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=12, null=True, blank=True , unique=True, validators=[validate_iranian_cellphone_number])
    email = models.EmailField(_("email address"), null=True, blank=True)  # nullable ایمیل
    is_staff = models.BooleanField(default=False)
    sms_verification=models.CharField(max_length=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    type = models.IntegerField(choices=UserType.choices, default=UserType.provider.value)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []  # چون حالا phone_number اصلی است، می‌توانید ایمیل را حذف کنید

    objects = UserManager()

    def __str__(self):
        return self.phone_number if self.phone_number else "کاربر بدون شماره"  # استفاده از شماره تلفن برای نمایش



class Profile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name="user_profile")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    image = models.ImageField(upload_to="profile/", default="profile/default.png")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_fullname(self):
        if self.first_name or self.last_name:
            return self.first_name + " " + self.last_name
        return "کاربر جدید"
    def save(self, *args, **kwargs):
        if self.user.type != UserType.provider.value:
            self.job = None
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

        
class VerificationCode(models.Model):
    phone_number = models.CharField(max_length=12, unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.code}"
    

