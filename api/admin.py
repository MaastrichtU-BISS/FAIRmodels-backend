from django.contrib import admin
from .models import Fairmodel, FairmodelVersion, VariableLink

admin.site.register(Fairmodel)
admin.site.register(FairmodelVersion)
admin.site.register(VariableLink)