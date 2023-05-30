from django.contrib import admin
from .models import *


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    list_filter = ("type",)
    list_display = ("id", "account", "type", 'created_at', 'updated_at')


@admin.register(StatementImage)
class StatementImageAdmin(admin.ModelAdmin):
    list_display = ("id", 'created_at', 'updated_at')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    pass


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    pass


