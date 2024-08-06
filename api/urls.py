from django.urls import path
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from .views import \
    index, \
    cedar_instances, \
    fairmodel_view, \
    fairmodels_view, \
    modelversions_view, \
    modelversion_view, \
    model_view, \
    variables_view

urlpatterns = [
    path('', api_view(['GET'])(authentication_classes([])(permission_classes([AllowAny])(index)))),
    path('cedar_instances/', cedar_instances),
    path('fairmodel/', fairmodels_view),
    path('fairmodel/<uuid:model_id>', fairmodel_view),
    path('fairmodel/<uuid:model_id>/version', modelversions_view),
    path('fairmodel/<uuid:model_id>/version/<uuid:version_id>', modelversion_view),
    # path('fairmodel/<uuid:model_id>/version/<uuid:version_id>/link', link_view),
    path('fairmodel/<uuid:model_id>/version/<uuid:version_id>/model', model_view),
    path('fairmodel/<uuid:model_id>/version/<uuid:version_id>/variables', variables_view)
]