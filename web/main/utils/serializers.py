from rest_framework.serializers import Serializer


class BaseSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ValidatorSerializer(BaseSerializer, object):
    @classmethod
    def check(cls, data, many=False, context=None):
        serializer = cls(data=data, many=many, context=context or {})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
