from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from commons.models import BaseModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('must have email')
        if not password:
            raise ValueError('must have password')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    objects = UserManager()

    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    profile_image_url = models.URLField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email if self.email else str(self.id)
