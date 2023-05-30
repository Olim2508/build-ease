from typing import Union, List

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from main.decorators import except_shell
from main.models import ProductCategory, VehicleType, WorkType
from . import serializers
from .choices import AccountChoice
from .models import Account, AccountImage, City
from .smsc_api import SMSC

User = get_user_model()


class UserService:
    @staticmethod
    def send_sms_code(time_otp, phone_number):
        smsc = SMSC()
        smsc.send_sms(
            str(phone_number), f"Ваш код подтверждения: {str(time_otp)}", sender="sms"
        )

    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user_by_phone(phone_number) -> Union[User, None]:
        return User.objects.get(phone_number=phone_number)

    @staticmethod
    def get_or_create_user(**kwargs):
        obj, created = User.objects.get_or_create(**kwargs)
        return obj

    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user_by_id(id):
        return User.objects.get(id=id)


class AccountService:
    @staticmethod
    @except_shell((ProductCategory.DoesNotExist,))
    def get_product_category(id: int):
        return ProductCategory.objects.get(id=id)

    @staticmethod
    @except_shell((City.DoesNotExist,))
    def get_city(id: int):
        return City.objects.get(id=id)

    @staticmethod
    @except_shell((Account.DoesNotExist,))
    def get_account_by_id(id: int):
        return Account.objects.get(id=id)

    @staticmethod
    @except_shell((VehicleType.DoesNotExist,))
    def get_vehicle_type(id: int):
        return VehicleType.objects.get(id=id)

    @staticmethod
    @except_shell((WorkType.DoesNotExist,))
    def get_work_type(id: int):
        return WorkType.objects.get(id=id)

    @staticmethod
    def create_provider_account(data: dict, user: User):
        product_category = AccountService.get_product_category(data['product_category'])
        city = AccountService.get_city(data['city'])
        del data['product_category']
        del data['city']
        images = data.pop("images") if data.get("images") else []
        account_provider = Account.objects.create(
            user=user,
            type=AccountChoice.PROVIDER,
            product_category=product_category,
            city=city,
            **data
        )
        # todo create images with bulk_create
        if images:
            for image in images:
                AccountImage.objects.create(
                    type=image['type'],
                    image=image['image'],
                    account=account_provider
                )

        return account_provider

    @staticmethod
    def create_courier_account(data: dict, user: User):
        vehicle_type = AccountService.get_vehicle_type(data['vehicle_type'])
        del data['vehicle_type']
        images = data.pop("images") if data.get("images") else []
        account_courier = Account.objects.create(
            user=user,
            type=AccountChoice.COURIER,
            vehicle_type=vehicle_type,
            **data
        )
        # todo create images with bulk_create
        if images:
            for image in images:
                AccountImage.objects.create(
                    type=image['type'],
                    image=image['image'],
                    account=account_courier
                )
        return account_courier

    @staticmethod
    def create_master_account(data: dict, user: User):
        work_type = AccountService.get_work_type(data['work_type'])
        del data['work_type']
        images = data.pop("images") if data.get("images") else []
        account_master = Account.objects.create(
            user=user,
            type=AccountChoice.MASTER,
            work_type=work_type,
            **data
        )
        # todo create images with bulk_create
        if images:
            for image in images:
                AccountImage.objects.create(
                    type=image['type'],
                    image=image['image'],
                    account=account_master
                )
        return account_master

    @staticmethod
    @except_shell((AccountImage.DoesNotExist,))
    def get_account_image_by_id(id):
        return AccountImage.objects.get(id=id)

    @staticmethod
    def update_account_images(images: List[dict]) -> None:
        for img in images:
            image_instance = AccountService.get_account_image_by_id(img['id'])
            image_instance.image = img['image']
            image_instance.type = img['type']
            image_instance.save()

    @staticmethod
    def get_account_list_by_ids(id_list: List[int]) -> QuerySet[Account]:
        return Account.objects.filter(id__in=id_list).order_by("-created_at")
