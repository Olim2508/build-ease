# Generated by Django 3.2.11 on 2023-04-05 07:47

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Категория товара',
                'verbose_name_plural': 'Категории товара',
            },
        ),
        migrations.CreateModel(
            name='Statement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('COU', 'Курьер'), ('MAS', 'Бригадир'), ('PRD', 'Материалы')], max_length=3, verbose_name='Тип заявки')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_not_accept_responses', models.BooleanField(blank=True, default=False, verbose_name='Не принимаю отклики')),
                ('is_in_work', models.BooleanField(blank=True, default=False, verbose_name='В работе')),
                ('is_turnkey_work', models.BooleanField(blank=True, null=True, verbose_name='Ремонт под ключ')),
                ('is_electric_work', models.BooleanField(blank=True, null=True, verbose_name='Электромонтажные работы')),
                ('is_plumbing_work', models.BooleanField(blank=True, null=True, verbose_name='Сантехнические работы')),
                ('is_finishing_work', models.BooleanField(blank=True, null=True, verbose_name='Отделочные работы')),
                ('is_floor_covering_work', models.BooleanField(blank=True, null=True, verbose_name='Укладка напольного покрытия')),
                ('is_installation_doors', models.BooleanField(blank=True, null=True, verbose_name='Установка межкомнатных дверей')),
                ('is_other_work', models.BooleanField(blank=True, null=True, verbose_name='Другой ремонт')),
                ('work_detail', models.TextField(blank=True, null=True, verbose_name='Описание работы')),
                ('department_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес помещения')),
                ('department_area', models.IntegerField(blank=True, null=True, verbose_name='Площадь помещения')),
                ('ceiling_height', models.IntegerField(blank=True, null=True, verbose_name='Высота потолка')),
                ('type_of_repair', models.CharField(blank=True, max_length=255, null=True, verbose_name='Вид ремонта')),
                ('repair_type', models.CharField(blank=True, choices=[('PRE', 'Премиум ремонт'), ('STD', 'Стандартный ремонт'), ('ECO', 'Эконом ремонт')], max_length=3, null=True, verbose_name='Тип ремонта')),
                ('current_state', models.CharField(blank=True, max_length=255, null=True, verbose_name='Текущее состояние')),
                ('budget_from', models.IntegerField(blank=True, null=True, verbose_name='Бюджет от')),
                ('budget_to', models.IntegerField(blank=True, null=True, verbose_name='Бюджет до')),
                ('date_of_start_construction', models.DateTimeField(blank=True, null=True, verbose_name='Дата начала ремонта')),
                ('additional_info', models.TextField(blank=True, null=True, verbose_name='Дополнительная информация')),
                ('repair_start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала ремонта')),
                ('from_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Откуда забрать')),
                ('to_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Куда привезти')),
                ('delivery_date', models.DateField(blank=True, null=True, verbose_name='Дата доставки')),
                ('delivery_time', models.TimeField(blank=True, null=True, verbose_name='Время доставки')),
                ('is_loaders_needed', models.BooleanField(blank=True, default=False, null=True, verbose_name='Нужны грузчики')),
                ('receiver_phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='Номер телефона получателя')),
                ('comment_to_delivery', models.TextField(blank=True, null=True, verbose_name='Комментарий к доставке')),
                ('delivery_price', models.IntegerField(blank=True, null=True, verbose_name='Стоимость доставки')),
                ('is_passing_cargo', models.BooleanField(blank=True, default=False, null=True, verbose_name='Попутный груз')),
                ('is_active', models.BooleanField(blank=True, default=True, null=True, verbose_name='Активный')),
                ('is_completed', models.BooleanField(blank=True, default=False, null=True, verbose_name='Завершен')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth_app.account')),
                ('product_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.productcategory', verbose_name='Категория строй материалов')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
            },
        ),
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Тип кузова',
                'verbose_name_plural': 'Типы кузова',
            },
        ),
        migrations.CreateModel(
            name='WorkType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Виды работ',
                'verbose_name_plural': 'Виды работ',
            },
        ),
        migrations.CreateModel(
            name='StatementImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='statement_images')),
                ('statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.statement')),
            ],
            options={
                'verbose_name': 'Изображения заявки',
                'verbose_name_plural': 'Изображения заявки',
            },
        ),
        migrations.AddField(
            model_name='statement',
            name='vehicle_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.vehicletype', verbose_name='Тип кузова'),
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(verbose_name='Цена')),
                ('is_viewed', models.BooleanField(blank=True, default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth_app.account', verbose_name='Аккаунт')),
                ('statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.statement', verbose_name='Заявка')),
            ],
            options={
                'verbose_name': 'Отклик',
                'verbose_name_plural': 'Отклики',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('is_moderated', models.BooleanField(default=False, verbose_name='Модерированный')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_ratings', to='auth_app.account', verbose_name='Пользователь')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worker_ratings', to='auth_app.account', verbose_name='Рабочий')),
            ],
        ),
    ]
