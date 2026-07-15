from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Красивая и удобная админка для CustomUser"""

    list_display = ('username', 'display_name', 'email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'display_name', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # Поля при просмотре пользователя
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('display_name', 'first_name', 'last_name', 'email', 'avatar', 'bio', 'phone')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined', 'last_activity')
        }),
    )

    # Поля при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'display_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login', 'last_activity')