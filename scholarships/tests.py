from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import ApplicantProfile, Application, Award, ScholarshipProgram

User = get_user_model()


@pytest.fixture
def users(db):
    users = {
        "reviewer": User.objects.create_user("reviewer", "reviewer@example.com", "StrongPassword123!", role="reviewer"),
        "applicant": User.objects.create_user("applicant", "applicant@example.com", "StrongPassword123!", role="applicant"),
        "other": User.objects.create_user("other", "other@example.com", "StrongPassword123!", role="applicant"),
    }
    ApplicantProfile.objects.create(user=users["applicant"], student_number="S1", school="University", gpa="3.8")
    ApplicantProfile.objects.create(user=users["other"], student_number="S2", school="University", gpa="3.7")
    return users


@pytest.fixture
def program(db):
    return ScholarshipProgram.objects.create(name="STEM", description="STEM award", amount="5000", slots=1, opens_at=timezone.now() - timedelta(days=1), closes_at=timezone.now() + timedelta(days=5))


def client_for(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=user).key}")
    return client


@pytest.mark.django_db
def test_registration_forces_applicant_and_creates_profile():
    payload = {"username": "new", "email": "new@example.com", "password": "VeryStrongPassword123!", "student_number": "S9", "school": "College", "gpa": "3.50", "role": "admin"}
    response = APIClient().post("/api/auth/register/", payload, format="json")
    assert response.status_code == 201
    assert response.data["data"]["user"]["role"] == "applicant"
    assert ApplicantProfile.objects.filter(student_number="S9").exists()


@pytest.mark.django_db
def test_application_window_and_duplicate_are_enforced(users, program):
    client = client_for(users["applicant"])
    payload = {"program": program.id, "statement": "My goals and record qualify me for this award."}
    assert client.post("/api/applications/", payload, format="json").status_code == 201
    assert client.post("/api/applications/", payload, format="json").status_code == 400


@pytest.mark.django_db
def test_applicant_cannot_see_another_application(users, program):
    application = Application.objects.create(reference="APP-PRIVATE", applicant=users["other"], program=program, statement="Private statement")
    assert client_for(users["applicant"]).get(f"/api/applications/{application.id}/").status_code == 404


@pytest.mark.django_db
def test_approval_creates_award_and_capacity_is_enforced(users, program):
    first = Application.objects.create(reference="APP-FIRST", applicant=users["applicant"], program=program, statement="First")
    second = Application.objects.create(reference="APP-SECOND", applicant=users["other"], program=program, statement="Second")
    reviewer = client_for(users["reviewer"])
    assert reviewer.patch(f"/api/applications/{first.id}/review/", {"status": "approved", "score": "95"}, format="json").status_code == 200
    assert reviewer.patch(f"/api/applications/{second.id}/review/", {"status": "approved", "score": "90"}, format="json").status_code == 400
    assert Award.objects.count() == 1


@pytest.mark.django_db
def test_terminal_application_cannot_be_reviewed_again(users, program):
    application = Application.objects.create(reference="APP-DONE", applicant=users["applicant"], program=program, statement="Done", status=Application.Status.REJECTED)
    response = client_for(users["reviewer"]).patch(f"/api/applications/{application.id}/review/", {"status": "approved"}, format="json")
    assert response.status_code == 400
