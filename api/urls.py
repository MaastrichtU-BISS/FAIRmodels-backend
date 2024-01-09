from django.urls import path
from .views import index, model_view, models_view, modelversions_view, modelversion_view

urlpatterns = [
    path('', index),
    path('model/', models_view),
    path('model/<int:model_id>', model_view),
    path('model/<int:model_id>/version', modelversions_view),
    path('model/<int:model_id>/version/<int:version_id>', modelversion_view),
]