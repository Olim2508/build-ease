from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


# def generate_key():
#     """User otp key generator"""
#     # key = pyotp.TOTP("base32secret3232", 4)
#     # code = key.now()
#     key = pyotp.random_base32()
#     if is_unique(key):
#         return key
#     generate_key()
#
#
# def is_unique(sms_code):
#     try:
#         User.objects.get(sms_code=sms_code)
#     except User.DoesNotExist:
#         return True
#     return False
#
#
# @receiver(pre_save, sender=User)
# def create_key(sender, instance, **kwargs):
#     """This creates the key for users that don't have keys"""
#     if not instance.sms_code:
#         instance.sms_code = generate_key()
