from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email')
    list_editable = ('role',)
    empty_value_display = '-пусто-'

    class Meta:
        model = User
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
