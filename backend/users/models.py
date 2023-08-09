from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель для создания пользователя foodgram."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=settings.LENGTH_OF_FIELDS_SHORT,
        unique=True,
    )
    username = models.CharField(
        'Никнейм',
        max_length=settings.LENGTH_OF_FIELDS_LONG,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.LENGTH_OF_FIELDS_SHORT,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LENGTH_OF_FIELDS_SHORT,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Follow(models.Model):
    """Модель подписки на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following'
    )

    class Meta:
        ordering = ('-id', )
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
