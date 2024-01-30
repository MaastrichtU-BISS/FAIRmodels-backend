from django.urls import path
from .views import index, fairmodel_view, fairmodels_view, modelversions_view, modelversion_view, model_view

urlpatterns = [
    path('', index),
    path('fairmodel/', fairmodels_view),
    path('fairmodel/<uuid:model_id>', fairmodel_view),
    path('fairmodel/<uuid:model_id>/version', modelversions_view),
    path('fairmodel/<uuid:model_id>/version/<uuid:version_id>', modelversion_view),
    path('fairmodel/<uuid:model_id>/version/<uuid:version_id>/model', model_view),
]