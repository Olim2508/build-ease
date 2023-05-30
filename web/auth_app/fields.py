import base64
import imghdr
import uuid

from rest_framework import serializers
from urllib3.packages import six
from django.core.files.base import ContentFile
from drf_yasg import openapi


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if "data:" in data and ";base64," in data:
                header, data = data.split(";base64,")

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_image")

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (
                file_name,
                file_extension,
            )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension

    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_STRING,
            "title": "Base64Image",
            "description": "Base64 Image",
            "readOnly": False,
        }

