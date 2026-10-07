from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from scholarships.models import ApplicantProfile, ScholarshipProgram

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        password = "ChangeMe123!"
        users = {}
        for username, role, email in [("admin", "admin", "admin@example.com"), ("reviewer", "reviewer", "reviewer@example.com"), ("applicant", "applicant", "applicant@example.com")]:
            user, created = User.objects.get_or_create(username=username, defaults={"email": email, "role": role})
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            users[username] = user
        ApplicantProfile.objects.get_or_create(user=users["applicant"], defaults={"student_number": "STU-001", "school": "Example University", "gpa": "3.75"})
        ScholarshipProgram.objects.get_or_create(name="Future Builders Scholarship", defaults={"description": "Supports high-potential students.", "amount": "5000.00", "slots": 3, "opens_at": timezone.now() - timedelta(days=1), "closes_at": timezone.now() + timedelta(days=30)})
        self.stdout.write(self.style.SUCCESS("Seed data is ready. Development password: ChangeMe123!"))
