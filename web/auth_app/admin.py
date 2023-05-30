from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from auth_app.models import Account, SmsCode, AccountImage, City

User = get_user_model()

admin.site.unregister(Group)
admin.site.register(City)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone_number", "is_phone_verified")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_filter = ("type",)
    list_display = ("id", "user", "type", "city", "created_at", "updated_at")


@admin.register(AccountImage)
class AccountImageAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "type", "image")


@admin.register(SmsCode)
class SmsCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "user")
