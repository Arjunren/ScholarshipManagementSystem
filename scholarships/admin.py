from django.contrib import admin
from .models import ApplicantProfile, Application, Award, ScholarshipProgram

admin.site.register([ApplicantProfile, ScholarshipProgram, Application, Award])

# Register your models here.
