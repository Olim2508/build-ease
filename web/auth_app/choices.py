from django.db.models import TextChoices


class AccountChoice(TextChoices):
    PROVIDER = ("PRO", "Поставщик")
    COURIER = ("COU", "Курьер")
    MASTER = ("MAS", "Бригадир")
    CLIENT = ("CLI", "Клиент")


class AccountImageChoice(TextChoices):
    STANDARD = ("STD", "Простой")
    PASSPORT = ("PAS", "Уд. личности")
    TECH_PASSPORT = ("TPS", "Тех.паспорт")
    MASTER_PHOTO = ("MPH", "Фото бригадира")
    DRIVING_LICENSE = ("DRV", "Водительское удостоверение")
    TRANSPORT_PHOTO = ("TRP", "Фото транспорта")
