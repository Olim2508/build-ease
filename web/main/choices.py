from django.db.models import TextChoices


class StatementChoice(TextChoices):
    COURIER = ("COU", "Курьер")
    MASTER = ("MAS", "Бригадир")
    PRODUCTS = ("PRD", "Материалы")


class RepairTypeChoice(TextChoices):
    PREMIUM = ("PRE", "Премиум ремонт")
    STANDARD = ("STD", "Стандартный ремонт")
    ECONOMY = ("ECO", "Эконом ремонт")


class CurrentStateChoice(TextChoices):
    PREMIUM = ("PRM", "Черновое")
    PREFINISHING = ("PRF", "Предчистовое")
    ECONOMY = ("ECO", "Эконом ремонт")


