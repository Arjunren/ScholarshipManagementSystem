from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from scholarships.models import ApplicantProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "is_active", "profile", "date_joined"]
        read_only_fields = fields

    def get_profile(self, obj):
        if not hasattr(obj, "applicant_profile"):
            return None
        profile = obj.applicant_profile
        return {"student_number": profile.student_number, "school": profile.school, "gpa": profile.gpa}


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    student_number = serializers.CharField(write_only=True)
    school = serializers.CharField(write_only=True)
    gpa = serializers.DecimalField(max_digits=3, decimal_places=2, min_value=0, max_value=4, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "student_number", "school", "gpa"]

    @transaction.atomic
    def create(self, validated_data):
        profile_data = {field: validated_data.pop(field) for field in ["student_number", "school", "gpa"]}
        user = User.objects.create_user(**validated_data, role=User.Role.APPLICANT)
        ApplicantProfile.objects.create(user=user, **profile_data)
        return user
