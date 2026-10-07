from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        REVIEWER = "reviewer", "Reviewer"
        APPLICANT = "applicant", "Applicant"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role, default=Role.APPLICANT, db_index=True)
    REQUIRED_FIELDS = ["email"]

# Create your models here.
