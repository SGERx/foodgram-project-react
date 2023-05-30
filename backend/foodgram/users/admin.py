from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscribtion


@admin.register(CustomUser)
class Admin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('email', 'first_name')


@admin.register(Subscribtion)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
