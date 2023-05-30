from typing import List

from django.conf import settings
from django.db.models import QuerySet, Avg
from django.db import transaction
from auth_app.models import Account
from main.choices import StatementChoice
from main.decorators import except_shell
from main.models import Statement, StatementImage, Response, Favourites, Rating


class StatementService:

    @staticmethod
    @except_shell((StatementImage.DoesNotExist,))
    def get_statement_image_by_id(id):
        return StatementImage.objects.get(id=id)

    @staticmethod
    @except_shell((Statement.DoesNotExist,))
    def get_statement_by_id(id):
        return Statement.objects.get(id=id)

    @staticmethod
    def create_product_statement(data: dict):
        from auth_app.services import AccountService
        account = AccountService.get_account_by_id(data.pop("account"))
        product_category = AccountService.get_product_category(data.pop("product_category"))
        images = data.pop("images") if data.get("images") else []

        statement = Statement.objects.create(type=StatementChoice.PRODUCTS,
                                             account=account, product_category=product_category, **data)
        StatementService.create_statement_images(statement, images)
        return statement

    @staticmethod
    def create_master_statement(data: dict):
        from auth_app.services import AccountService
        account = AccountService.get_account_by_id(data.pop("account"))
        images = data.pop("images") if data.get("images") else []

        statement = Statement.objects.create(type=StatementChoice.MASTER,
                                             account=account, **data)
        StatementService.create_statement_images(statement, images)
        return statement

    @staticmethod
    def create_courier_statement(data: dict):
        from auth_app.services import AccountService
        account = AccountService.get_account_by_id(data.pop("account"))
        vehicle_type = AccountService.get_vehicle_type(data.pop("vehicle_type"))
        statement = Statement.objects.create(type=StatementChoice.COURIER,
                                             account=account, vehicle_type=vehicle_type, **data)
        return statement

    @staticmethod
    def create_statement_images(statement: Statement, images: list):
        if images:
            image_list = [
                StatementImage(statement=statement, image=image['image']) for image in images
            ]
            StatementImage.objects.bulk_create(image_list)

    @staticmethod
    def delete_statement_image(img_id: StatementImage) -> None:
        StatementImage.objects.get(id=img_id).delete()

    @staticmethod
    def create_statement_image(img, statement: Statement) -> None:
        StatementImage.objects.create(image=img, statement=statement)

    @staticmethod
    def update_statement_images(images: list, statement: Statement):
        with transaction.atomic():
            for img in images:
                if img.get("id") and not img.get("image"):  # delete image
                    StatementService.delete_statement_image(img.get("id"))
                elif not img.get("id") and img.get("image"):  # create new image
                    StatementService.create_statement_image(img.get("image"), statement)
                else:  # update existing image
                    image_instance = StatementService.get_statement_image_by_id(img['id'])
                    image_instance.image = img['image']
                    image_instance.save()

    @staticmethod
    def populate_image_base_url(image_url: str) -> str:
        if settings.STAGE == "PROD":
            if image_url.startswith('/'):
                image_url = image_url[1:]
            if not settings.BASE_API_URL.endswith('/'):
                settings.BASE_API_URL += '/'
            return settings.BASE_API_URL + image_url
        return image_url


class ResponseService:

    @staticmethod
    @except_shell((Response.DoesNotExist,))
    def get_response_by_id(response_id):
        return Response.objects.get(id=response_id)

    @staticmethod
    def create_response(data):
        from auth_app.services import AccountService
        statement = StatementService.get_statement_by_id(data.pop("statement"))
        account = AccountService.get_account_by_id(data.pop("account"))
        response = Response.objects.create(
            account=account,
            statement=statement,
            **data
        )
        return response

    @staticmethod
    def get_statement_ids_of_account_response(account: Account):
        response_statement_ids = Response.objects.filter(account=account).values_list("statement_id").distinct()
        return [item[0] for item in response_statement_ids]


class FavoriteService:

    @staticmethod
    def add_account_to_favorite(base_account, adding_account):
        Favourites.objects.create(
            added_by_account=base_account,
            favorite_account=adding_account
        )

    @staticmethod
    def delete_account_from_favorite(base_account, adding_account):
        Favourites.objects.get(added_by_account=base_account, favorite_account=adding_account).delete()

    @staticmethod
    def get_favorite_accounts_of_user(account: Account) -> QuerySet[Account]:
        from auth_app.services import AccountService
        account_id_list = Favourites.objects.filter(added_by_account=account).values_list('favorite_account_id')
        accounts_qs = AccountService.get_account_list_by_ids(account_id_list)
        return accounts_qs


class RatingService:

    @staticmethod
    def create_rating(client, data):
        from auth_app.services import AccountService
        worker = AccountService.get_account_by_id(data.pop("worker"))
        Rating.objects.create(
            client=client,
            worker=worker,
            **data
        )

    @staticmethod
    def get_account_average_rating(account: Account):
        rating_average = Rating.objects.filter(worker=account).aggregate(rating_avg=Avg("rate"))
        return rating_average['rating_avg']


