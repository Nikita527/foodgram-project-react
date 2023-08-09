from django.contrib import admin
from django.contrib.admin import register

from users.models import Follow, User


@register(User)
class MyUserAdmin(admin.ModelAdmin):
    list_display = (
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
        'first_name',
        'email',
    )
    ordering = ('username',)
    empty_value_display = '-пусто-'
    save_on_top = True


@register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    list_filter = (
        'user',
        'author',
    )
    empty_value_display = '-пусто-'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('user', 'author')
        return qs
