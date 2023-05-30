import random

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField

from auth_app import choices
from auth_app.querysets import ConfirmationQuerySet
from main.models import ProductCategory, VehicleType, WorkType, BaseModel


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField("Email address", null=True, blank=True, unique=True)
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    # todo need to delete field sms_code
    sms_code = models.CharField(unique=True, max_length=100, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    object = UserManager()

    def get_full_name(self) -> str:
        return super().get_full_name()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.phone_number} {self.email}"


class SmsCode(models.Model):
    code = models.CharField(max_length=20, verbose_name='Код подтверждения')
    expires_at = models.DateTimeField(verbose_name='Срок действия')
    user = models.ForeignKey(User, models.CASCADE, verbose_name='Пользователь')
    is_used = models.BooleanField(default=False, verbose_name='Был использован?')

    objects = ConfirmationQuerySet.as_manager()

    def save(self, *args, **kwargs):
        # TODO change code
        # self.code = str(random.randint(1000, 9999))
        self.code = '0000'
        self.expires_at = timezone.now() + timedelta(hours=2)
        return super().save(*args, **kwargs)


class Account(BaseModel):
    full_name = models.CharField("Имя", max_length=255, null=True, blank=True)
    city = models.ForeignKey("auth_app.City", on_delete=models.SET_NULL, related_name="accounts", null=True, blank=True,
                             verbose_name="Город")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    type = models.CharField(
        "Тип аккаунта",
        choices=choices.AccountChoice.choices,
        default=choices.AccountChoice.CLIENT,
        max_length=3,
    )
    avatar = models.ImageField(upload_to="images/avatars", null=True, blank=True, verbose_name="Аватар")

    # поля Поставшика
    provider_name = models.CharField(
        "Наименование поставщика", max_length=255, null=True, blank=True
    )
    product_category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True, verbose_name="Категория товара"
    )
    provider_address = models.CharField(
        "Адрес поставщика", max_length=255, null=True, blank=True
    )

    # поля Курьера
    courier_company_name = models.CharField(
        "Наименование компании", max_length=255, null=True, blank=True
    )
    vehicle_brand = models.CharField(
        "Марка и модель транспорта", max_length=255, null=True, blank=True
    )
    state_number = models.CharField("Гос.номер", max_length=255, null=True, blank=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, verbose_name="Тип кузова")
    car_color = models.CharField("Цвет машины", max_length=255, null=True, blank=True)

    # поля Бригадира
    about_me = models.CharField("О себе", max_length=255, null=True, blank=True)
    experience = models.CharField("Опыт работы", max_length=255, null=True, blank=True)
    work_type = models.ForeignKey(WorkType, on_delete=models.SET_NULL, null=True, verbose_name="Виды работ")
    number_of_objects = models.IntegerField(
        "Количество объектов может брать одновременно", null=True, blank=True
    )
    price_per_metre_square = models.IntegerField(
        "Стоимость кв.метра", null=True, blank=True
    )
    is_safe_deal = models.BooleanField(
        "Безопасная сделка", default=False, null=True, blank=True
    )

    def __str__(self):
        return f"{self.id}- {self.user.phone_number}"

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"


class AccountImage(models.Model):
    account = models.ForeignKey("auth_app.Account", on_delete=models.CASCADE, related_name='account_images')
    type = models.CharField(max_length=255,
                            choices=choices.AccountImageChoice.choices, default=choices.AccountImageChoice.STANDARD)
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return f"{self.account} -- {self.type}"


class City(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Город"


class DeviceUser(BaseModel):
    user = models.ForeignKey("auth_app.User", on_delete=models.CASCADE)
    token = models.CharField(verbose_name="Токен", max_length=255)

    def __str__(self):
        return f"user-{self.user.id}, token-{self.token}"

