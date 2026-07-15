from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Кастомная модель пользователя для TeamFlow"""

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("Пользователь с такой почтой уже существует."),
        }
    )

    display_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Отображаемое имя"
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="О себе"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )

    # Дополнительные настройки
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']

    def __str__(self):
        return self.display_name or self.get_full_name() or self.username

    def get_full_name(self):
        full_name = super().get_full_name()
        return full_name.strip() if full_name else self.username