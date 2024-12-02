from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    nickname = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'accounts_user'