from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Patient, MedicalHistory, Prediction

admin.site.register(Patient)
admin.site.register(MedicalHistory)
admin.site.register(Prediction)