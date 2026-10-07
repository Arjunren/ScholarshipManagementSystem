from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ApplicantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applicant_profile")
    student_number = models.CharField(max_length=50, unique=True)
    school = models.CharField(max_length=200)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(4)])


class ScholarshipProgram(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    slots = models.PositiveIntegerField()
    opens_at = models.DateTimeField(db_index=True)
    closes_at = models.DateTimeField(db_index=True)
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Application(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    reference = models.CharField(max_length=24, unique=True)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="scholarship_applications")
    program = models.ForeignKey(ScholarshipProgram, on_delete=models.PROTECT, related_name="applications")
    statement = models.TextField()
    status = models.CharField(max_length=20, choices=Status, default=Status.SUBMITTED, db_index=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="reviewed_applications")
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["applicant", "program"], name="unique_applicant_program")]


class Award(models.Model):
    application = models.OneToOneField(Application, on_delete=models.PROTECT, related_name="award")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    awarded_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
