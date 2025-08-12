from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    is_doctor = models.BooleanField(default= False)

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username