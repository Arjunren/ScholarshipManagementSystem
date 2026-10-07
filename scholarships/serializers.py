from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Application, Award, ScholarshipProgram
from .services import submit_application


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipProgram
        fields = ["id", "name", "description", "amount", "slots", "opens_at", "closes_at", "active", "created_at"]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        opens_at = attrs.get("opens_at", getattr(self.instance, "opens_at", None))
        closes_at = attrs.get("closes_at", getattr(self.instance, "closes_at", None))
        if opens_at and closes_at and closes_at <= opens_at:
            raise serializers.ValidationError({"closes_at": "Closing time must be after opening time."})
        if attrs.get("amount", 1) <= 0 or attrs.get("slots", 1) < 1:
            raise serializers.ValidationError("Amount and slots must be positive.")
        return attrs


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ["amount", "awarded_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_detail = UserSerializer(source="applicant", read_only=True)
    program_detail = ProgramSerializer(source="program", read_only=True)
    award = AwardSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ["id", "reference", "applicant_detail", "program", "program_detail", "statement", "status", "score", "reviewed_by", "review_notes", "award", "created_at", "updated_at"]
        read_only_fields = ["reference", "status", "score", "reviewed_by", "review_notes", "created_at", "updated_at"]

    def create(self, validated_data):
        return submit_application(applicant=self.context["request"].user, **validated_data)


class ReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[Application.Status.UNDER_REVIEW, Application.Status.APPROVED, Application.Status.REJECTED])
    score = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100, required=False, allow_null=True)
    review_notes = serializers.CharField(required=False, allow_blank=True)
