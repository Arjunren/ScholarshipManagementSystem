import secrets

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Application, Award, ScholarshipProgram


def _reference():
    return f"APP-{secrets.token_hex(5).upper()}"


@transaction.atomic
def submit_application(*, applicant, program, statement):
    program = ScholarshipProgram.objects.select_for_update().get(pk=program.pk)
    now = timezone.now()
    if not program.active or not (program.opens_at <= now <= program.closes_at):
        raise ValidationError({"program": "This scholarship is not accepting applications."})
    if not hasattr(applicant, "applicant_profile"):
        raise ValidationError({"applicant": "An applicant profile is required."})
    try:
        return Application.objects.create(reference=_reference(), applicant=applicant, program=program, statement=statement)
    except IntegrityError as exc:
        raise ValidationError({"program": "You have already applied to this program."}) from exc


@transaction.atomic
def review_application(*, application, reviewer, new_status, score=None, review_notes=""):
    application = Application.objects.select_for_update().select_related("program").get(pk=application.pk)
    program = ScholarshipProgram.objects.select_for_update().get(pk=application.program_id)
    allowed = {
        Application.Status.SUBMITTED: {Application.Status.UNDER_REVIEW, Application.Status.APPROVED, Application.Status.REJECTED},
        Application.Status.UNDER_REVIEW: {Application.Status.APPROVED, Application.Status.REJECTED},
        Application.Status.APPROVED: set(), Application.Status.REJECTED: set(), Application.Status.WITHDRAWN: set(),
    }
    if new_status not in allowed[application.status]:
        raise ValidationError({"status": f"Cannot change {application.status} to {new_status}."})
    if new_status == Application.Status.APPROVED:
        approved = Application.objects.filter(program=program, status=Application.Status.APPROVED).exclude(pk=application.pk).count()
        if approved >= program.slots:
            raise ValidationError({"status": "All scholarship slots have already been awarded."})
        Award.objects.get_or_create(application=application, defaults={"amount": program.amount})
    application.status = new_status
    application.score = score
    application.review_notes = review_notes
    application.reviewed_by = reviewer
    application.save(update_fields=["status", "score", "review_notes", "reviewed_by", "updated_at"])
    return application


@transaction.atomic
def withdraw_application(*, application):
    application = Application.objects.select_for_update().get(pk=application.pk)
    if application.status not in {Application.Status.SUBMITTED, Application.Status.UNDER_REVIEW}:
        raise ValidationError({"status": "Only pending applications can be withdrawn."})
    application.status = Application.Status.WITHDRAWN
    application.save(update_fields=["status", "updated_at"])
    return application
