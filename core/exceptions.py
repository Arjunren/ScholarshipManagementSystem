from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response({"error": {"code": "SERVER_ERROR", "message": "Request could not be completed"}}, status=500)
    validation = isinstance(exc, ValidationError)
    response.data = {"error": {"code": "VALIDATION_ERROR" if validation else str(getattr(exc, "default_code", "REQUEST_ERROR")).upper(), "message": "Invalid request data" if validation else str(getattr(exc, "detail", "Request could not be completed")), "details": response.data if validation else None}}
    return response
