from django.core.exceptions import ValidationError
import re

def validate_iranian_cellphone_number(value):
    pattern = r'^09\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError('Enter a valid Iranian cellphone number.')


def validate_national_code(value):
    """
    Validator for Iranian national code (کد ملی).
    Ensures that the national code is exactly 10 digits long.
    """
    if not re.match(r'^\d{10}$', value):
        raise ValidationError('کد ملی باید شامل 10 رقم باشد.')

def validate_iban(value):
    """
    Validator for Iranian IBAN (شماره شبا).
    Ensures that the IBAN starts with 'IR' and is exactly 24 characters long.
    """
    if not re.match(r'^IR\d{22}$', value):
        raise ValidationError('شماره شبا باید با IR شروع شود و شامل 24 کاراکتر باشد.')

def validate_bank_card_number(value):
    """
    Validator for Iranian bank card number (شماره کارت بانکی).
    Ensures that the bank card number is exactly 16 digits long.
    """
    if not re.match(r'^\d{16}$', value):
        raise ValidationError('شماره کارت بانکی باید شامل 16 رقم باشد.')
    
def validate_fixed_phone(value):
    # بررسی اینکه شماره فقط شامل اعداد باشد
    if not re.match(r'^\d+$', value):
        raise ValidationError('شماره تلفن ثابت باید فقط شامل اعداد باشد.')
