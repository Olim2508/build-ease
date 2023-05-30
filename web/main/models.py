from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from . import choices


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class ProductCategory(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товара"


class VehicleType(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип кузова"
        verbose_name_plural = "Типы кузова"


class WorkType(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Виды работ"
        verbose_name_plural = "Виды работ"


class Statement(BaseModel):
    account = models.ForeignKey("auth_app.Account", on_delete=models.CASCADE)
    type = models.CharField(
        "Тип заявки",
        choices=choices.StatementChoice.choices,
        max_length=3,
    )
    is_not_accept_responses = models.BooleanField(verbose_name="Не принимаю отклики", default=False, blank=True)
    is_in_work = models.BooleanField(verbose_name="В работе", default=False, blank=True)

    # заявка клиента к бригадиру
    is_turnkey_work = models.BooleanField(null=True, blank=True, verbose_name="Ремонт под ключ")
    is_electric_work = models.BooleanField(null=True, blank=True, verbose_name="Электромонтажные работы")
    is_plumbing_work = models.BooleanField(null=True, blank=True, verbose_name="Сантехнические работы")
    is_finishing_work = models.BooleanField(null=True, blank=True, verbose_name="Отделочные работы")
    is_floor_covering_work = models.BooleanField(null=True, blank=True, verbose_name="Укладка напольного покрытия")
    is_installation_doors = models.BooleanField(null=True, blank=True, verbose_name="Установка межкомнатных дверей")
    is_other_work = models.BooleanField(null=True, blank=True, verbose_name="Другой ремонт")

    work_detail = models.TextField(verbose_name="Описание работы", null=True, blank=True)
    department_address = models.CharField(verbose_name="Адрес помещения", null=True, blank=True, max_length=255)
    department_area = models.IntegerField(verbose_name="Площадь помещения", null=True, blank=True)
    ceiling_height = models.IntegerField(verbose_name="Высота потолка", null=True, blank=True)
    type_of_repair = models.CharField(verbose_name="Вид ремонта", null=True, blank=True, max_length=255)
    repair_type = models.CharField(
        verbose_name="Тип ремонта",
        choices=choices.RepairTypeChoice.choices,
        max_length=3,
        null=True,
        blank=True,
    )
    current_state = models.CharField(verbose_name="Текущее состояние", null=True, blank=True, max_length=255)
    budget_from = models.IntegerField(verbose_name="Бюджет от", null=True, blank=True)
    budget_to = models.IntegerField(verbose_name="Бюджет до", null=True, blank=True)
    date_of_start_construction = models.DateTimeField(verbose_name="Дата начала ремонта", null=True, blank=True)

    # additional_info - используется и при заявке на сторойматериалов
    additional_info = models.TextField(verbose_name="Дополнительная информация", null=True, blank=True)
    repair_start_date = models.DateField(null=True, blank=True, verbose_name="Дата начала ремонта")
    # заявка на курьера
    from_address = models.CharField(verbose_name="Откуда забрать", null=True, blank=True, max_length=255)

    # эти поля используются и при заявке на сторойматериалов
    to_address = models.CharField(verbose_name="Куда привезти", null=True, blank=True, max_length=255)
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Дата доставки")
    delivery_time = models.TimeField(null=True, blank=True, verbose_name="Время доставки")
    is_loaders_needed = models.BooleanField(default=False, null=True, blank=True, verbose_name="Нужны грузчики")
    loaders_count = models.IntegerField(verbose_name="Количество грузчиков", null=True, blank=True, default=0)

    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, verbose_name="Тип кузова")
    receiver_phone_number = PhoneNumberField(blank=True, null=True, verbose_name="Номер телефона получателя")
    comment_to_delivery = models.TextField(verbose_name="Комментарий к доставке", null=True, blank=True)
    delivery_price = models.IntegerField(verbose_name="Стоимость доставки", null=True, blank=True)
    is_passing_cargo = models.BooleanField(default=False, null=True, blank=True, verbose_name="Попутный груз")

    # заявка на стройматериалов
    product_category = models.ForeignKey("main.ProductCategory", on_delete=models.SET_NULL,
                                         null=True, blank=True, verbose_name="Категория строй материалов")

    is_active = models.BooleanField(verbose_name="Активный", null=True, blank=True, default=True)
    is_completed = models.BooleanField(verbose_name="Завершен", null=True, blank=True, default=False)
    # is_canceled = models.BooleanField(verbose_name="Отменен", null=True, blank=True, default=False)
    # cancellation_detail = models.OneToOneField('main.CancellationDetail', verbose_name="Причина отказа", null=True, blank=True, on_delete=models.SET_NULL)
    executor = models.ForeignKey("auth_app.Account", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Исполнитель", related_name="statements")

    def __str__(self):
        return f"{self.account.user.phone_number} (id: {self.id})"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


# class CancellationDetail(BaseModel):
#     cancelled_by = models.OneToOneField('auth_app.Account', verbose_name="Отменил аккаунт", on_delete=models.CASCADE)


class StatementImage(BaseModel):
    statement = models.ForeignKey("main.Statement", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="statement_images")

    def __str__(self):
        return f"{self.statement} -- id: {self.id}"

    class Meta:
        verbose_name = "Изображения заявки"
        verbose_name_plural = "Изображения заявки"


class Response(BaseModel):
    account = models.ForeignKey("auth_app.Account", on_delete=models.CASCADE, verbose_name="Аккаунт")
    statement = models.ForeignKey("main.Statement", on_delete=models.CASCADE, verbose_name="Заявка")
    price = models.IntegerField(verbose_name="Цена", null=True, blank=True)
    is_viewed = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"

    def __str__(self):
        return f"id-{self.id}, Заявка - {self.statement.id}, Аккаунт - {self.account.id}"


class Rating(BaseModel):
    rate = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    is_moderated = models.BooleanField(default=False, verbose_name="Модерированный")
    client = models.ForeignKey('auth_app.Account', on_delete=models.CASCADE, verbose_name="Пользователь", related_name="client_ratings")
    worker = models.ForeignKey('auth_app.Account', on_delete=models.CASCADE, verbose_name="Рабочий", related_name="worker_ratings")


class Favourites(BaseModel):
    added_by_account = models.ForeignKey('auth_app.Account', on_delete=models.CASCADE, verbose_name="Добавил аккаунт",
                                         related_name="favourite_added_by_account")
    favorite_account = models.ForeignKey('auth_app.Account', on_delete=models.CASCADE, verbose_name="Избранный аккаунт",
                                         related_name="favorite_favorite_account")

    class Meta:
        verbose_name = "Избранный аккаунт"
        verbose_name_plural = "Избранные аккаунты"

    def __str__(self):
        return f"Добавил аккаунт - {self.added_by_account.id}, Избранный аккаунт - {self.favorite_account.id}"

