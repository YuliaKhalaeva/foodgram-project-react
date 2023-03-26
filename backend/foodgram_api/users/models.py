from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_api import settings


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    USER_ROLES = [
        (ADMIN, 'Admin role'),
        (USER, 'User role'),
    ]
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, verbose_name='Name')
    last_name = models.CharField(max_length=150, verbose_name='Surname')
    role = models.CharField(
        max_length=10,
        choices=USER_ROLES,
        default='user',
    )

    class Meta:
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == self.USER

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='author',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriber',
    )

    class Meta:
        verbose_name = 'Favorite author'
        verbose_name_plural = 'Favorite authors'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscribe_users'
            )
        ]