from django.urls import path, include
from .models import Fairmodel
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class FairmodelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fairmodel
        fields = ['id', 'name', 'description']

# ViewSets define the view behavior.
class FairmodelViewSet(viewsets.ModelViewSet):
    queryset = Fairmodel.objects.all()
    serializer_class = FairmodelSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'model', FairmodelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]