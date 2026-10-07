from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsProgramAdmin, IsReviewer
from .models import Application, Award, ScholarshipProgram
from .serializers import ApplicationSerializer, ProgramSerializer, ReviewSerializer
from .services import review_application, withdraw_application

User = get_user_model()


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipProgram.objects.all().order_by("-created_at")
    serializer_class = ProgramSerializer
    search_fields = ["name", "description"]
    ordering_fields = ["name", "amount", "slots", "opens_at", "closes_at"]

    def get_permissions(self):
        return [permissions.IsAuthenticated()] if self.action in {"list", "retrieve"} else [IsProgramAdmin()]


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]
    search_fields = ["reference", "applicant__username", "program__name"]
    ordering_fields = ["created_at", "score", "updated_at"]

    def get_queryset(self):
        queryset = Application.objects.select_related("applicant", "applicant__applicant_profile", "program", "reviewed_by").select_related("award")
        if self.request.user.role == User.Role.APPLICANT:
            queryset = queryset.filter(applicant=self.request.user)
        if self.request.query_params.get("status"):
            queryset = queryset.filter(status=self.request.query_params["status"])
        return queryset.order_by("-created_at")

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        if self.action == "review":
            return [IsReviewer()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.APPLICANT:
            self.permission_denied(self.request, message="Only applicants can submit applications.")
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH", detail="Use the review or withdraw action for status changes.")

    @action(detail=True, methods=["patch"])
    def review(self, request, pk=None):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review_data = dict(serializer.validated_data)
        new_status = review_data.pop("status")
        application = review_application(application=self.get_object(), reviewer=request.user, new_status=new_status, **review_data)
        return Response({"data": ApplicationSerializer(application, context={"request": request}).data})

    @action(detail=True, methods=["patch"])
    def withdraw(self, request, pk=None):
        application = self.get_object()
        if request.user.role != User.Role.APPLICANT or application.applicant_id != request.user.id:
            self.permission_denied(request)
        application = withdraw_application(application=application)
        return Response({"data": ApplicationSerializer(application, context={"request": request}).data})


class DashboardView(APIView):
    permission_classes = [IsReviewer]

    def get(self, request):
        statuses = Application.objects.values("status").annotate(total=Count("id")).order_by("status")
        awarded = Award.objects.aggregate(total=Sum("amount"))["total"] or 0
        return Response({"data": {"applications": list(statuses), "total_awarded": awarded, "programs": ScholarshipProgram.objects.count()}})

# Create your views here.
