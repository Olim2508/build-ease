from django.contrib.auth import get_user_model
from django.test import tag
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from auth_app.models import DeviceUser, SmsCode, City
from main.models import ProductCategory

User = get_user_model()


@tag('user')
class UserTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_login(self):
        url = reverse_lazy('auth_app:log-in')
        data = {'phone_number': "+998914344554"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(User.objects.filter(phone_number=data['phone_number']))

        device_token = "5f6aa01d"
        data = {'phone_number': "+998909899009", "device_token": device_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(User.objects.filter(phone_number=data['phone_number']))
        d_user = DeviceUser.objects.filter(token=device_token).first()
        self.assertEqual(d_user.token, device_token)


@tag('account')
class AccountTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product_category = ProductCategory.objects.create(title="sement")
        cls.city = City.objects.create(title="Buxoro")

    def setUp(self):
        url = reverse_lazy('auth_app:log-in')
        phone_number = "+998914076350"
        data = {'phone_number': phone_number}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        sms_code = SmsCode.objects.filter(is_used=False, user__phone_number=phone_number).first()
        url = reverse_lazy('auth_app:code-verify')
        verify_data = {**data, "code": sms_code.code}
        response = self.client.post(url, verify_data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["user"]["access_token"]}')

    def test_create_provider_account(self):
        url = reverse_lazy("auth_app:provider-list")
        # todo add image and avatar fields to test
        data = {
            "provider_name": "Mega Stroy",
            "product_category": 100,
            "city": self.city.id,
            "about_me": "tovaroya saxashban xas",
            "provider_address": "Kolxoz bozor",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json()['product_category'], ['Product category 100 does not exist'])
        data['product_category'] = self.product_category.id
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

