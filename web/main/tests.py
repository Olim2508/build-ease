from django.contrib.auth import get_user_model
from django.test import tag
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from auth_app import choices
from auth_app.choices import AccountChoice
from auth_app.models import SmsCode, Account
from main.models import ProductCategory, VehicleType, Favourites, Statement, Response as ResponseModel, Rating
from main.serializers import error_messages
from urllib.parse import urlencode

import base64

User = get_user_model()


@tag('favorites')
class FavoritesTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get_or_create(phone_number='+998914076350', email=None)[0]
        cls.user_2 = User.objects.get_or_create(phone_number='+998912122332', email=None)[0]
        cls.user_3 = User.objects.get_or_create(phone_number='+998913433443', email=None)[0]

        cls.client_account = Account.objects.create(
            full_name="John Snow",
            user=cls.user
        )

        cls.product_category = ProductCategory.objects.create(title="sement")
        cls.provider_account = Account.objects.create(
            type=AccountChoice.PROVIDER,
            provider_name="Stroy market",
            product_category=cls.product_category,
            provider_address="mustaqillik",
            user=cls.user_2
        )
        cls.provider_account_2 = Account.objects.create(
            type=AccountChoice.PROVIDER,
            provider_name="Mega stroy",
            product_category=cls.product_category,
            provider_address="alpomish",
            user=cls.user_3
        )

        cls.vehicle_type = VehicleType.objects.create(title="sedan")
        cls.courier_account = Account.objects.create(
            type=AccountChoice.COURIER,
            courier_company_name="yandex",
            vehicle_brand='bmw',
            state_number="777AAA",
            vehicle_type=cls.vehicle_type,
            car_color="black",
            user=cls.user_3
        )

    def setUp(self):
        url = reverse_lazy('auth_app:log-in')
        data = {'phone_number': self.user.phone_number}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        sms_code = SmsCode.objects.filter(is_used=False, user__phone_number=self.user.phone_number).first()
        url = reverse_lazy('auth_app:code-verify')
        verify_data = {**data, "code": sms_code.code}
        response = self.client.post(url, verify_data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["user"]["access_token"]}')
        self.client.credentials(HTTP_ACCOUNT_ID=str(self.client_account.id))

    def test_add_to_favorite(self):
        url = reverse_lazy("main:favorites-add_account_to_favorites")
        data = {
            "account_id": 100
        }
        self.assertEqual(Favourites.objects.count(), 0)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        data = {
            "account_id": self.provider_account.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(Favourites.objects.count(), 1)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json().get("account_id"), [error_messages['already_in_favorites']], response.data)

    def test_delete_from_favorite(self):
        url = reverse_lazy("main:favorites-add_account_to_favorites")
        data = {
            "account_id": self.provider_account.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(Favourites.objects.count(), 1)

        url = reverse_lazy("main:favorites-delete_account_from_favorites")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(Favourites.objects.count(), 0)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json().get("account_id"), [error_messages['not_in_favorites']], response.data)

    def test_get_favorite_accounts(self):
        Favourites.objects.create(added_by_account=self.client_account, favorite_account=self.provider_account)
        Favourites.objects.create(added_by_account=self.client_account, favorite_account=self.provider_account_2)
        Favourites.objects.create(added_by_account=self.client_account, favorite_account=self.courier_account)

        url = reverse_lazy("main:favorites-get_list")
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 3)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response = self.client.get(url, data={"type": choices.AccountChoice.PROVIDER})
        self.assertEqual(response.json()['count'], 2)

        response = self.client.get(url, data={"type": choices.AccountChoice.COURIER})
        self.assertEqual(response.json()['count'], 1)


@tag('statements-from-client-account')
class StatementsClientTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get_or_create(phone_number='+998914076350', email=None)[0]
        cls.user_2 = User.objects.get_or_create(phone_number='+998912122332', email=None)[0]
        cls.user_3 = User.objects.get_or_create(phone_number='+998913433443', email=None)[0]

        cls.client_account = Account.objects.create(
            full_name="John Snow",
            user=cls.user
        )

        cls.product_category = ProductCategory.objects.create(title="sement")
        cls.provider_account = Account.objects.create(
            type=AccountChoice.PROVIDER,
            provider_name="Stroy market",
            product_category=cls.product_category,
            provider_address="mustaqillik",
            user=cls.user_2
        )
        cls.provider_account_2 = Account.objects.create(
            type=AccountChoice.PROVIDER,
            provider_name="Mega stroy",
            product_category=cls.product_category,
            provider_address="alpomish",
            user=cls.user_3
        )

        cls.vehicle_type = VehicleType.objects.create(title="sedan")
        cls.courier_account = Account.objects.create(
            type=AccountChoice.COURIER,
            courier_company_name="yandex",
            vehicle_brand='bmw',
            state_number="777AAA",
            vehicle_type=cls.vehicle_type,
            car_color="black",
            user=cls.user_3
        )

    def setUp(self):
        url = reverse_lazy('auth_app:log-in')
        data = {'phone_number': self.user.phone_number}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        sms_code = SmsCode.objects.filter(is_used=False, user__phone_number=self.user.phone_number).first()
        url = reverse_lazy('auth_app:code-verify')
        verify_data = {**data, "code": sms_code.code}
        response = self.client.post(url, verify_data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["user"]["access_token"]}')
        self.client.credentials(HTTP_ACCOUNT_ID=str(self.client_account.id))

    def test_accept_executor_of_product_statement(self):
        statement = Statement.objects.create(
            account=self.client_account,
            product_category=self.product_category,
            to_address="Buxoro",
            delivery_date="2023-08-25",
            delivery_time="12:00",
            additional_info="test info",
            is_loaders_needed=False,
        )
        response_1 = ResponseModel.objects.create(
            account=self.provider_account,
            statement=statement,
            price="2000"
        )
        url = reverse_lazy("main:statement-product_statement_accept_executor")
        data = {
            "response_id": 100,
            "statement_id": statement.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json()['non_field_errors'], ["Response with this id does not exist"])
        data = {
            "response_id": response_1.id,
            "statement_id": 100
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json()['non_field_errors'], ["Statement 100 does not exist"])

        data = {
            "response_id": response_1.id,
            "statement_id": statement.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json()['message'], "accepted as executor")
        statement = Statement.objects.get(id=statement.id)
        self.assertEqual(statement.executor, self.provider_account)

        data = {
            "response_id": response_1.id,
            "statement_id": statement.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json()['non_field_errors'], ["Already accepted this executor"])

    def test_my_statements_list(self):
        Statement.objects.create(
            account=self.client_account,
            product_category=self.product_category,
            to_address="Buxoro",
            delivery_date="2023-08-25",
            delivery_time="12:00",
            additional_info="test info",
            is_loaders_needed=False,
            is_active=True,
            is_completed=False
        )
        Statement.objects.create(
            account=self.client_account,
            product_category=self.product_category,
            to_address="Toshkent",
            delivery_date="2023-08-25",
            delivery_time="12:00",
            additional_info="test info",
            is_loaders_needed=False,
            is_active=False,
            is_completed=False
        )
        Statement.objects.create(
            account=self.client_account,
            product_category=self.product_category,
            to_address="Samarqand",
            delivery_date="2023-08-25",
            delivery_time="12:00",
            additional_info="test info",
            is_loaders_needed=False,
            is_active=True,
            is_completed=True
        )
        url = reverse_lazy("main:statement-my_statements_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json()['count'], 3)

        url = reverse_lazy("main:statement-my_statements_list") + "?is_active=True"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json()['count'], 2)

        url = reverse_lazy("main:statement-my_statements_list") + "?is_completed=True"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json()['count'], 1)
        item = response.json()['results'][0]
        self.assertEqual(item['product_category']['id'], self.product_category.id)
        self.assertEqual(item['product_category']['title'], self.product_category.title)

    def test_create_product_statement(self):
        url = reverse_lazy("main:product-statement-list")
        # with open("test_images/img_1.jpg", "rb") as image_file:
        #     image_data = image_file.read()
        # data = {
        #     "account": self.client_account.id,
        #     "product_category": self.product_category.id,
        #     "to_address": "NY, Brooklyn",
        #     "delivery_date": "2023-08-25",
        #     "delivery_time": "15:00:00",
        #     "additional_info": "asdasdasd",
        #     "is_loaders_needed": True,
        #     "loaders_count": 2,
        #     "images": [
        #         {
        #             "image": base64.b64encode(image_data)
        #         },
        #     ],
        # }
        # response = self.client.post(url, data)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)


@tag('statements-from-provider-account')
class StatementsProviderTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get_or_create(phone_number='+998914076350', email=None)[0]
        cls.user_2 = User.objects.get_or_create(phone_number='+998912122332', email=None)[0]
        cls.user_4 = User.objects.get_or_create(phone_number='+998934544554', email=None)[0]

        cls.client_account = Account.objects.create(
            full_name="John Snow",
            user=cls.user
        )

        cls.client_account_2 = Account.objects.create(
            full_name="James Bond",
            user=cls.user_4
        )

        cls.product_category = ProductCategory.objects.create(title="sement")
        cls.product_category_2 = ProductCategory.objects.create(title="kraska")
        cls.provider_account = Account.objects.create(
            type=AccountChoice.PROVIDER,
            provider_name="Stroy market",
            product_category=cls.product_category,
            provider_address="mustaqillik",
            user=cls.user_2
        )

        cls.statement_1 = Statement.objects.create(
            account=cls.client_account,
            product_category=cls.product_category,
            to_address="Buxoro",
            delivery_date="2023-08-25",
            delivery_time="12:00",
            additional_info="test info",
            is_loaders_needed=False,
            executor=cls.provider_account,
            is_active=False
        )

        cls.statement_2 = Statement.objects.create(
            account=cls.client_account_2,
            product_category=cls.product_category_2,
            to_address="Toshkent",
            delivery_date="2023-08-25",
            delivery_time="12:00",
            additional_info="test info statement 2",
            is_loaders_needed=False,
            executor=cls.provider_account
        )

    def setUp(self):
        url = reverse_lazy('auth_app:log-in')
        data = {'phone_number': self.user_2.phone_number}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        sms_code = SmsCode.objects.filter(is_used=False, user__phone_number=self.user_2.phone_number).first()
        url = reverse_lazy('auth_app:code-verify')
        verify_data = {**data, "code": sms_code.code}
        response = self.client.post(url, verify_data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["user"]["access_token"]}')
        self.client.credentials(HTTP_ACCOUNT_ID=str(self.provider_account.id))

    def test_accepted_statements_list(self):
        url = reverse_lazy("main:statement-accepted_statements_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json()['count'], Statement.objects.filter(executor=self.provider_account).count())

    def test_new_statements_list(self):
        statement_3 = Statement.objects.create(
            account=self.client_account_2,
            product_category=self.product_category_2,
            to_address="Astana",
            delivery_date="2023-08-25",
            delivery_time="12:00",
            additional_info="test info statement 3",
            is_loaders_needed=False,
        )

        url = reverse_lazy("main:statement-new_statements_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(Statement.objects.count(), response.json()['count'])
        self.assertEqual(response.json()['results'][0]['product_category']['title'], self.product_category_2.title)

        ResponseModel.objects.create(statement=self.statement_1, account=self.provider_account, price=200)
        ResponseModel.objects.create(statement=self.statement_2, account=self.provider_account, price=300)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(1, response.json()['count'])
        # query_params = {
        #     "product_category": f"{self.product_category_2.id}"
        # }
        # url = reverse_lazy("main:statement-new_statements_list") + "?" + urlencode(query_params)
        # self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        # self.assertEqual(response.json()['count'], 2)


@tag('rating')
class RatingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.get_or_create(phone_number='+998914076350', email=None)[0]
        cls.user_2 = User.objects.get_or_create(phone_number='+998912122332', email=None)[0]
        cls.user_3 = User.objects.get_or_create(phone_number='+998934544554', email=None)[0]

        cls.client_account = Account.objects.create(
            full_name="John Snow",
            user=cls.user_1,
            type=AccountChoice.CLIENT,
        )

        cls.client_account_2 = Account.objects.create(
            full_name="James Bond",
            user=cls.user_2,
            type=AccountChoice.CLIENT,
        )

        cls.product_category = ProductCategory.objects.create(title="sement")
        cls.provider_account = Account.objects.create(
            type=AccountChoice.PROVIDER,
            provider_name="Stroy market",
            product_category=cls.product_category,
            provider_address="mustaqillik",
            user=cls.user_3
        )

    def setUp(self):
        url = reverse_lazy('auth_app:log-in')
        data = {'phone_number': self.user_1.phone_number}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        sms_code = SmsCode.objects.filter(is_used=False, user__phone_number=self.user_1.phone_number).first()
        url = reverse_lazy('auth_app:code-verify')
        verify_data = {**data, "code": sms_code.code}
        response = self.client.post(url, verify_data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["user"]["access_token"]}')
        self.client.credentials(HTTP_ACCOUNT_ID=str(self.client_account.id))

    def test_create_rating(self):
        url = reverse_lazy('main:rating-create')
        data = {
            "rate": 3,
            "description": "norm",
            "worker": 100,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        data['worker'] = self.provider_account.id
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json()['worker'], ['Rating already added to this account'], response.data)

    def test_get_list_of_ratings(self):
        url = reverse_lazy('main:rating-list', (self.provider_account.id, ))
        Rating.objects.create(client=self.client_account, worker=self.provider_account, rate=3, description="desc 1")
        Rating.objects.create(client=self.client_account_2, worker=self.provider_account, rate=4, description="test des")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.json()['count'], 2)

