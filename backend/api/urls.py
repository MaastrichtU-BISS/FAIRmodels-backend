from django.urls import path, include
from .models import Fairmodel, Fairmodel_Version
from rest_framework import routers, serializers, viewsets

class FairmodelVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fairmodel_Version()
        fields = ['fairmodel', 'version', 'onnx_model', 'update_description', 'created_at']

# Serializers define the API representation.
class FairmodelSerializer(serializers.HyperlinkedModelSerializer):
    fairmodel_version_set = FairmodelVersionSerializer(read_only=True, many=True)
    class Meta:
        model = Fairmodel()
        fields = ['id', 'name', 'description', 'fairmodel_version_set']

# ViewSets define the view behavior.
class FairmodelViewSet(viewsets.ModelViewSet):
    queryset = Fairmodel.objects.all()
    serializer_class = FairmodelSerializer

class FairmodelVersionViewSet(viewsets.ModelViewSet):
    queryset = Fairmodel_Version.objects.all()
    serializer_class = FairmodelVersionSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'model', FairmodelViewSet)
router.register(r'model_version', FairmodelVersionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]