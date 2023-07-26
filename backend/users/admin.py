from django.contrib import admin
from django.contrib.admin import register

from users.models import User


@register(User)
class MyUserAdmin(admin.ModelAdmin):
    list_display = (
        'is_active',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'is_active',
        'first_name',
        'email',
    )
    ordering = ('username',)
    empty_value_display = '-пусто-'
    save_on_top = True
