from django.contrib import admin

# Register your models here.
from .models import Fairmodel, Fairmodel_Version

admin.site.register(Fairmodel)
admin.site.register(Fairmodel_Version)