
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from auth_app.choices import AccountChoice, AccountImageChoice
from auth_app.fields import Base64ImageField
from auth_app.models import Account, SmsCode, AccountImage, City, DeviceUser
from main.models import ProductCategory, Rating
from main.services import RatingService, StatementService

User = get_user_model()

error_messages = {
    "not_active": "Your account is not active",
    "password_not_match": "The two password fields didn't match",
    "not_exists": "User with this phone number does not exists",
    "not_exists_user": "User with this id does not exists",
    "wrong_code": "Предоставленный код не совпадает или истек срок действия",
    "already_exists": "Phone number already exists",
}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "last_name", "id"]


class LogInSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    device_token = serializers.CharField(required=False)

    def save(self):
        from auth_app.services import UserService
        device_token = self.validated_data.pop("device_token") if self.validated_data.get("device_token") else None

        user = UserService.get_or_create_user(**self.validated_data, email=None)
        sms_code = SmsCode.objects.create(user=user)
        if device_token:
            DeviceUser.objects.create(user=user, token=device_token)
        print(sms_code.code)
        # UserService.send_sms_code(sms_code.code, user.phone_number)


class VerifyCodeSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    code = serializers.CharField(required=True)

    def validate_phone_number(self, phone_number):
        from auth_app.services import UserService

        user = UserService.get_user_by_phone(phone_number)
        if not user:
            raise serializers.ValidationError(error_messages["not_exists"])
        return phone_number

    def validate(self, data):
        if not SmsCode.objects.verify(data.get('phone_number'), data.get('code')):
            raise serializers.ValidationError(error_messages["wrong_code"])
        return data

    def save(self, **kwargs):
        from auth_app.services import UserService

        user = UserService.get_user_by_phone(self.validated_data["phone_number"])
        user.is_phone_verified = True
        user.save()
        SmsCode.objects.filter(
            user__phone_number=self.validated_data["phone_number"],
            code=self.validated_data["code"],
            expires_at__date=timezone.now().date(),
        ).update(is_used=True)
        self.validated_data["user"] = user


class ClientAccountSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(min_length=3, required=True)
    avatar = Base64ImageField(use_url=True, required=True, allow_empty_file=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['city'] = {"id": instance.city.id, "title": instance.city.title}
        return ret

    def create(self, validated_data):
        account = Account.objects.create(
            user=self.context["request"].user,
            type=AccountChoice.CLIENT,
            **validated_data
        )
        return account

    class Meta:
        model = Account
        fields = ["id", "full_name", "city", "avatar"]


class AccountImageSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=AccountImageChoice.choices, default=AccountImageChoice.STANDARD)
    image = Base64ImageField(use_url=True, required=True, allow_empty_file=False)


class AccountImageUpdateSerializer(AccountImageSerializer):
    id = serializers.IntegerField(required=True)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class ProviderAccountSerializer(serializers.Serializer):
    provider_name = serializers.CharField(min_length=3, required=True)
    product_category = serializers.IntegerField(required=True, write_only=True)
    city = serializers.IntegerField(required=True, write_only=True)
    about_me = serializers.CharField(min_length=3, required=True)
    provider_address = serializers.CharField(min_length=3, required=True)
    images = serializers.ListField(child=AccountImageSerializer(), required=False)
    avatar = Base64ImageField(use_url=True, required=False, allow_empty_file=False, allow_null=True)

    def validate_product_category(self, product_category):
        from auth_app.services import AccountService

        product_category_item = AccountService.get_product_category(product_category)
        if not product_category_item:
            raise serializers.ValidationError([f"Product category {product_category} does not exist"])
        return product_category

    def validate_city(self, city):
        from auth_app.services import AccountService

        city_item = AccountService.get_city(city)
        if not city_item:
            raise serializers.ValidationError([f"City {city} does not exist"])
        return city

    def to_representation(self, instance):
        from main.serializers import ProductCategorySerializer
        ret = super().to_representation(instance)
        ret['id'] = instance.id
        ret['product_category'] = ProductCategorySerializer(instance.product_category).data
        ret['city'] = CitySerializer(instance.city).data
        ret['images'] = AccountImageUpdateSerializer(instance.account_images, many=True).data
        return ret

    def create(self, validated_data):
        from auth_app.services import AccountService

        return AccountService.create_provider_account(validated_data, self.context["request"].user)

    class Meta:
        model = Account
        fields = ["id", "provider_name", "product_category", "city", "provider_address", 'avatar']


class ProviderAccountUpdateSerializer(ProviderAccountSerializer):
    images = serializers.ListField(child=AccountImageUpdateSerializer(), required=False)

    def validate(self, attrs):
        from auth_app.services import AccountService

        if images := attrs.get("images"):
            for i in images:
                img_item = AccountService.get_account_image_by_id(i['id'])
                if not img_item:
                    raise serializers.ValidationError(f"Image {i['id']} does not exist")
        return attrs

    def update(self, instance, validated_data):
        from auth_app.services import AccountService

        category = AccountService.get_product_category(validated_data.pop('product_category'))
        instance.product_category = category
        images = validated_data.pop("images") if validated_data.get("images") else []
        if images:
            AccountService.update_account_images(images)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CourierAccountSerializer(serializers.Serializer):
    courier_company_name = serializers.CharField(min_length=3, required=True)
    vehicle_brand = serializers.CharField(min_length=3, required=True)
    state_number = serializers.CharField(min_length=3, required=True)
    vehicle_type = serializers.IntegerField(required=True, write_only=True)
    car_color = serializers.CharField(min_length=3, required=True)
    images = serializers.ListField(child=AccountImageSerializer(), required=False)
    avatar = Base64ImageField(use_url=True, required=False, allow_empty_file=False, allow_null=True)

    def validate_vehicle_type(self, vehicle_type):
        from auth_app.services import AccountService

        vehicle_type_item = AccountService.get_vehicle_type(vehicle_type)
        if not vehicle_type_item:
            raise serializers.ValidationError([f"Vehicle Type {vehicle_type} does not exist"])
        return vehicle_type

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(
            {
                "id": instance.id,
                "vehicle_type": {
                    "id": instance.vehicle_type.id,
                    "title": instance.vehicle_type.title,
                }
            }
        )
        ret['images'] = AccountImageUpdateSerializer(instance.account_images, many=True).data
        return ret

    def create(self, validated_data):
        from auth_app.services import AccountService

        return AccountService.create_courier_account(validated_data, self.context["request"].user)

    class Meta:
        model = Account
        fields = ["id", "courier_company_name", "vehicle_brand", "state_number", "vehicle_type", "car_color", "avatar"]


class CourierAccountUpdateSerializer(CourierAccountSerializer):
    images = serializers.ListField(child=AccountImageUpdateSerializer(), required=False)

    def validate(self, attrs):
        if images := attrs.get("images"):
            for i in images:
                from auth_app.services import AccountService

                img_item = AccountService.get_account_image_by_id(i['id'])
                if not img_item:
                    raise serializers.ValidationError(f"Image {i['id']} does not exist")
        return attrs

    def update(self, instance, validated_data):
        from auth_app.services import AccountService

        vehicle_type = AccountService.get_vehicle_type(validated_data.pop('vehicle_type'))
        instance.vehicle_type = vehicle_type
        images = validated_data.pop("images") if validated_data.get("images") else []
        if images:
            AccountService.update_account_images(images)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MasterAccountSerializer(serializers.Serializer):
    full_name = serializers.CharField(min_length=3, required=True)
    experience = serializers.CharField(min_length=3, required=True)
    about_me = serializers.CharField(min_length=3, required=True)
    work_type = serializers.IntegerField(required=True, write_only=True)
    number_of_objects = serializers.IntegerField(required=True)
    images = serializers.ListField(child=AccountImageSerializer(), required=False)
    avatar = Base64ImageField(use_url=True, required=False, allow_empty_file=False, allow_null=True)

    def validate_work_type(self, work_type):
        from auth_app.services import AccountService

        work_type_item = AccountService.get_work_type(work_type)
        if not work_type_item:
            raise serializers.ValidationError([f"Work Type {work_type} does not exist"])
        return work_type

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(
            {
                "id": instance.id,
                "work_type": {
                    "id": instance.work_type.id,
                    "title": instance.work_type.title,
                }
            }
        )
        ret['images'] = AccountImageUpdateSerializer(instance.account_images, many=True).data
        return ret

    def create(self, validated_data):
        from auth_app.services import AccountService

        return AccountService.create_master_account(validated_data, self.context["request"].user)


class MasterAccountUpdateSerializer(MasterAccountSerializer):
    images = serializers.ListField(child=AccountImageUpdateSerializer(), required=False)

    def validate(self, attrs):
        if images := attrs.get("images"):
            for i in images:
                from auth_app.services import AccountService

                img_item = AccountService.get_account_image_by_id(i['id'])
                if not img_item:
                    raise serializers.ValidationError(f"Image {i['id']} does not exist")
        return attrs

    def update(self, instance, validated_data):
        from auth_app.services import AccountService

        work_type = AccountService.get_work_type(validated_data.pop('work_type'))
        instance.work_type = work_type
        images = validated_data.pop("images") if validated_data.get("images") else []
        if images:
            AccountService.update_account_images(images)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductCategorySerialiser(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerialiser()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['images'] = AccountImageSerializer(instance.account_images, many=True).data
        data['avatar'] = StatementService.populate_image_base_url(instance.avatar.url) if instance.avatar else None
        data['average_rating'] = RatingService.get_account_average_rating(instance)
        data['ratings_count'] = Rating.objects.filter(worker=instance).count()
        return data

    class Meta:
        model = Account
        fields = ["id", "full_name", "type", "provider_name", "courier_company_name", "product_category"]


class AccountListSerializer(serializers.ModelSerializer):
    product_category = ProductCategorySerialiser()

    class Meta:
        model = Account
        fields = '__all__'


class UserJWTSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=355)
    refresh_token = serializers.CharField(max_length=355)
    user = UserSerializer()
