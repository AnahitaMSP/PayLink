from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from accounts.validators import validate_iranian_cellphone_number,validate_national_code,validate_iban,validate_bank_card_number,validate_fixed_phone
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
        user.save(using=self._db) 
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
    REQUIRED_FIELDS = [] 
    objects = UserManager()

    def __str__(self):
        return self.phone_number if self.phone_number else "کاربر بدون شماره" 

class Province(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    tel_prefix = models.CharField(max_length=10, null=True, blank=True)
    def __str__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=255)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name

class Specialty(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class SubSpecialty(models.Model):  
    name = models.CharField(max_length=255, unique=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='subspecialties')

    def __str__(self):
        return f"{self.name} - {self.specialty.name}"



class Profile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name="user_profile")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    job = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    image = models.ImageField(upload_to="profile/", default="profile/default.png", null=True, blank=True)
    national_code = models.CharField(
        max_length=10,
        validators=[validate_national_code],
        unique=True,
        null=True,
        blank=True
    )
    iban = models.CharField(
        max_length=24,
        validators=[validate_iban],
        unique=True,
        null=True,
        blank=True
    )
    bank_card_number = models.CharField(
        max_length=16,
        validators=[validate_bank_card_number],
        unique=True,
        null=True,
        blank=True
    )

    specialties = models.ForeignKey(Specialty,on_delete=models.CASCADE , blank=True,null=True, related_name='profiles')
    sub_specialties = models.ForeignKey(SubSpecialty,on_delete=models.CASCADE , blank=True,null=True, related_name='profiles')



    province = models.ForeignKey(Province, on_delete=models.CASCADE ,null=True, blank=True)  
    city = models.ForeignKey(City, on_delete=models.CASCADE,null=True, blank=True) 
    address = models.CharField(max_length=200,null=True, blank=True) 
    tell_phone = models.CharField(
        max_length=15,
        validators=[validate_fixed_phone] ,null=True, blank=True 
    )
    gender = models.CharField(max_length=10, choices=[('male', 'مرد'), ('female', 'زن'), ('other', 'سایر')],null=True, blank=True)
    visit_fee = models.DecimalField(max_digits=200, decimal_places=0, default=0)
    
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

class Task(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True ,related_name='profile')  # ارتباط با پزشک

    name = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=200, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.fee}"    
    
        
class VerificationCode(models.Model):
    phone_number = models.CharField(max_length=12, unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.code}"
    

