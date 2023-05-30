import json

from rest_framework import serializers
from auth_app.serializers import AccountSerializer

from auth_app.fields import Base64ImageField
from auth_app.models import Account
from auth_app.services import AccountService
from chats.models import Message, Conversation
from main import choices
from main.models import ProductCategory, VehicleType, WorkType, Statement, Rating, Favourites, Response
from main.services import StatementService, ResponseService
from phonenumber_field.serializerfields import PhoneNumberField
from main.utils.serializers import ValidatorSerializer

error_messages = {
    "already_in_favorites": "Account already exists in favorites",
    "not_in_favorites": "Account does not exist in favorites",
    "response_not_exist": "Response with this id does not exist",
    "rating_already_added": "Rating already added to this account",
}


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = "__all__"


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = "__all__"


class StatementImageSerializer(serializers.Serializer):
    image = Base64ImageField(use_url=True, required=False, allow_empty_file=False)


class StatementImageUpdateSerializer(StatementImageSerializer):
    id = serializers.IntegerField(required=False)


class StatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statement
        fields = "__all__"


class StatementToRepresentationSerializer(StatementSerializer):
    product_category = ProductCategorySerializer()
    account = AccountSerializer()


class MyStatementSerializer(StatementSerializer):
    account = AccountSerializer()
    statementimage_set = StatementImageUpdateSerializer(many=True)
    responses_count_all = serializers.IntegerField()
    responses_count_not_viewed = serializers.IntegerField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update({
            "product_category": {
                "id": instance.product_category.id,
                "title": instance.product_category.title,
            },
        })
        return ret


class NewStatementsSerializer(StatementSerializer):
    is_response_added = serializers.BooleanField()


class ProductStatementSerializer(serializers.Serializer):
    account = serializers.IntegerField(required=True, write_only=True)
    product_category = serializers.IntegerField(required=True, write_only=True)
    to_address = serializers.CharField(min_length=3, required=True)
    delivery_date = serializers.DateField(required=True)
    delivery_time = serializers.TimeField(required=True)
    additional_info = serializers.CharField(required=True)
    is_loaders_needed = serializers.BooleanField(required=True)
    loaders_count = serializers.IntegerField(required=False)
    images = serializers.ListField(child=StatementImageSerializer(), required=False)

    def validate_account(self, account: int):
        account_obj = AccountService.get_account_by_id(account)
        if not account_obj:
            raise serializers.ValidationError(f"Account {account} does not exist")
        return account

    def validate_product_category(self, product_category: int):
        product_category_obj = AccountService.get_product_category(product_category)
        if not product_category_obj:
            raise serializers.ValidationError(f"Product category {product_category} does not exist")
        return product_category

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(
            {
                "id": instance.id,
                "product_category": {
                    "id": instance.product_category.id,
                    "title": instance.product_category.title,
                },
                "account": {
                    "id": instance.account.id,
                    "full_name": instance.account.full_name,
                }
            }
        )
        image_list = [
            {
                "id": i.id,
                "image": StatementService.populate_image_base_url(i.image.url)
            } for i in instance.statementimage_set.all()
        ]
        ret.update({"images": image_list, "created_at": instance.created_at})
        return ret

    def create(self, validated_data):
        return StatementService.create_product_statement(validated_data)


class ProductStatementUpdateSerializer(ProductStatementSerializer):
    images = serializers.ListField(child=StatementImageUpdateSerializer(), required=False)

    def validate(self, attrs):
        if images := attrs.get("images"):
            for i in images:
                if i.get("id"):
                    img_item = StatementService.get_statement_image_by_id(i['id'])
                    if not img_item:
                        raise serializers.ValidationError(f"Image {i['id']} does not exist")
        return attrs

    def update(self, instance, validated_data):
        product_category = AccountService.get_product_category(validated_data.pop('product_category'))
        account = AccountService.get_account_by_id(validated_data.pop('account'))
        instance.product_category = product_category
        instance.account = account
        images = validated_data.pop("images") if validated_data.get("images") else []
        if images:
            StatementService.update_statement_images(images, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MasterStatementSerializer(serializers.Serializer):
    account = serializers.IntegerField(required=True, write_only=True)
    type_of_repair = serializers.CharField(min_length=3, required=True)
    current_state = serializers.CharField(min_length=3, required=True)
    repair_type = serializers.ChoiceField(choices=choices.RepairTypeChoice.choices,
                                          default=choices.RepairTypeChoice.STANDARD)
    department_area = serializers.IntegerField(required=True, write_only=True)
    ceiling_height = serializers.IntegerField(required=True, write_only=True)
    additional_info = serializers.CharField(min_length=3, required=True)
    budget_from = serializers.IntegerField(required=True, write_only=True)
    budget_to = serializers.IntegerField(required=True, write_only=True)
    images = serializers.ListField(child=StatementImageSerializer(), required=False)

    def validate_account(self, account: int):
        account_obj = AccountService.get_account_by_id(account)
        if not account_obj:
            raise serializers.ValidationError(f"Account {account} does not exist")
        return account

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(
            {
                "id": instance.id,
                "account": {
                    "id": instance.account.id,
                    "full_name": instance.account.full_name,
                }
            }
        )
        image_list = [
            {
                "id": i.id,
                "image": i.image.url
            } for i in instance.statementimage_set.all()
        ]
        ret.update({"images": image_list, "created_at": instance.created_at})
        return ret

    def create(self, validated_data):
        return StatementService.create_master_statement(validated_data)


class MasterStatementUpdateSerializer(MasterStatementSerializer):
    images = serializers.ListField(child=StatementImageUpdateSerializer(), required=False)

    def validate(self, attrs):
        if images := attrs.get("images"):
            for i in images:
                if i.get("id"):
                    img_item = StatementService.get_statement_image_by_id(i['id'])
                    if not img_item:
                        raise serializers.ValidationError(f"Image {i['id']} does not exist")
        return attrs

    def update(self, instance, validated_data):
        account = AccountService.get_account_by_id(validated_data.pop('account'))
        instance.account = account
        images = validated_data.pop("images") if validated_data.get("images") else []
        if images:
            StatementService.update_statement_images(images, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ResponseSerializer(serializers.Serializer):
    account = serializers.IntegerField(write_only=True, required=True)
    statement = serializers.IntegerField(write_only=True, required=True)
    price = serializers.IntegerField(required=True, min_value=1)

    def validate_account(self, account: int):
        account_obj = AccountService.get_account_by_id(account)
        if not account_obj:
            raise serializers.ValidationError(f"Account {account} does not exist")
        return account

    def validate_statement(self, statement: int):
        statement_obj = StatementService.get_statement_by_id(statement)
        if not statement_obj:
            raise serializers.ValidationError(f"Statement {statement} does not exist")
        return statement

    def create(self, validated_data):
        return ResponseService.create_response(validated_data)

    def update(self, instance, validated_data):
        statement = StatementService.get_statement_by_id(validated_data.pop('statement'))
        account = AccountService.get_account_by_id(validated_data.pop('account'))
        instance.statement = statement
        instance.account = account
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(
            {
                "id": instance.id,
                "statement": {
                    "id": instance.statement.id,
                },
                "account": {
                    "id": instance.account.id,
                    "full_name": instance.account.full_name,
                }
            }
        )
        return ret


class ResponseListSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = Response
        fields = ["id", "account", "price", "is_viewed", "statement"]


class StatementAcceptResponseSerializer(serializers.Serializer):
    is_not_accept_responses = serializers.BooleanField(required=True)

    def save(self, **kwargs):
        instance = self.context['instance']
        instance.is_not_accept_responses = self.validated_data['is_not_accept_responses']
        instance.save()


class ConversationSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ("id", "name")


class ChatResponseSerializer(serializers.ModelSerializer):
    conversation = ConversationSimpleSerializer(read_only=True)

    def create(self, data):
        statement = StatementService.get_statement_by_id(data.pop("statement").id)
        account = AccountService.get_account_by_id(data.pop("account").id)
        conversation_name = f'{sorted([statement.account.id, account.id])[0]}__{sorted([statement.account.id, account.id])[1]}'
        response = Response.objects.create(
            account=account,
            statement=statement,
        )
        conversation = Conversation.objects.get_or_create(name=conversation_name)
        Message.objects.get_or_create(
            statement=statement,
            defaults={
                'from_user': statement.account,
                'to_user': account,
                'conversation': conversation[0],
            }
        )
        return {"id": response.id, "statement": statement, "account": account,
                "conversation": conversation[0]}

    class Meta:
        model = Response
        fields = ('id', 'statement', 'account', 'statement', 'account', "conversation",)


class AcceptProductStatementExecutor(serializers.Serializer):
    response_id = serializers.IntegerField(required=True)
    statement_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        statement = StatementService.get_statement_by_id(attrs['statement_id'])
        if not statement:
            raise serializers.ValidationError(f"Statement {attrs['statement_id']} does not exist")
        if statement.account != self.context['request'].account:
            raise serializers.ValidationError(f"Statement is not created by current account")
        response_instance = ResponseService.get_response_by_id(attrs['response_id'])
        if not response_instance:
            raise serializers.ValidationError(error_messages['response_not_exist'])
        # otklika in zayavkaba namondagi
        if response_instance.statement.id != statement.id:
            raise serializers.ValidationError("Response is not made to this statement")

        if statement.executor and statement.executor.id == response_instance.account.id:
            raise serializers.ValidationError("Already accepted this executor")
        return attrs

    def save(self, **kwargs):
        response_instance = ResponseService.get_response_by_id(self.validated_data["response_id"])
        statement = StatementService.get_statement_by_id(self.validated_data['statement_id'])
        statement.executor = response_instance.account
        statement.is_not_accept_responses = True
        statement.save()


class RatingSerializer(serializers.Serializer):
    is_moderated = serializers.BooleanField(read_only=True)
    worker = serializers.IntegerField(required=True)
    description = serializers.CharField(required=True)
    rate = serializers.IntegerField(required=True)

    def validate_worker(self, worker_id):
        worker_account = AccountService.get_account_by_id(worker_id)
        if not worker_account:
            raise serializers.ValidationError(f"Account {worker_id} does not exist")
        request_account = self.context['request'].account
        if Rating.objects.filter(client=request_account, worker=worker_account).exists():
            raise serializers.ValidationError([error_messages['rating_already_added']])
        return worker_id


class RatingListSerializer(serializers.ModelSerializer):
    worker = AccountSerializer()

    class Meta:
        model = Rating
        fields = '__all__'


# class RatingFilterSerializer(ValidatorSerializer):
#     worker = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())


class CourierStatementSerializer(serializers.Serializer):
    account = serializers.IntegerField(required=True, write_only=True)
    from_address = serializers.CharField(min_length=3, required=True)
    to_address = serializers.CharField(min_length=3, required=True)
    delivery_date = serializers.DateField(required=True)
    delivery_time = serializers.TimeField(required=True)
    vehicle_type = serializers.IntegerField(required=True, write_only=True)
    receiver_phone_number = PhoneNumberField(required=True)
    comment_to_delivery = serializers.CharField(min_length=3, required=True)
    delivery_price = serializers.IntegerField(required=True)
    is_passing_cargo = serializers.BooleanField(required=True)
    is_loaders_needed = serializers.BooleanField(required=True)

    def validate_account(self, account: int):
        account_obj = AccountService.get_account_by_id(account)
        if not account_obj:
            raise serializers.ValidationError(f"Account {account} does not exist")
        return account

    def validate_vehicle_type(self, vehicle_type: int):
        vehicle_type_obj = AccountService.get_vehicle_type(vehicle_type)
        if not vehicle_type_obj:
            raise serializers.ValidationError(f"Vehicle type {vehicle_type} does not exist")
        return vehicle_type

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.update(
            {
                "id": instance.id,
                "vehicle_type": {
                    "id": instance.vehicle_type.id,
                    "title": instance.vehicle_type.title,
                },
                "account": {
                    "id": instance.account.id,
                    "full_name": instance.account.full_name,
                }
            }
        )
        return ret

    def create(self, validated_data):
        return StatementService.create_courier_statement(validated_data)

    def update(self, instance, validated_data):
        vehicle_type = AccountService.get_vehicle_type(validated_data.pop('vehicle_type'))
        account = AccountService.get_account_by_id(validated_data.pop('account'))
        instance.vehicle_type = vehicle_type
        instance.account = account
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FavoritesSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        if not self.context['request'].headers.get("Account-ID"):
            raise serializers.ValidationError(f"Add user account id in headers")
        return attrs

    def validate_account_id(self, account_id):
        account = AccountService.get_account_by_id(account_id)
        if not account:
            raise serializers.ValidationError(f"Account {account_id} does not exist")
        request_account = self.context['request'].account
        if Favourites.objects.filter(added_by_account=request_account, favorite_account_id=account_id).exists():
            raise serializers.ValidationError([error_messages['already_in_favorites']])
        return account_id


class FavoritesDeleteSerializer(FavoritesSerializer):

    def validate_account_id(self, account_id):
        account = AccountService.get_account_by_id(account_id)
        if not account:
            raise serializers.ValidationError(f"Account {account_id} does not exist")
        request_account = self.context['request'].account
        if not Favourites.objects.filter(added_by_account=request_account, favorite_account_id=account_id).exists():
            raise serializers.ValidationError([error_messages['not_in_favorites']])
        return account_id
