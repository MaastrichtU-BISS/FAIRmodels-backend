from rest_framework import serializers
from .models import Fairmodel, FairmodelVersion

class FairmodelSerializer(serializers.ModelSerializer):

    def create(self):
        request = self.context.get("request")
        fm = Fairmodel()
        fm.name = self.validated_data['name']
        fm.description = self.validated_data['description']
        fm.user = request.user
        fm.save()
        return fm
        
    class Meta:
        model = Fairmodel
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}
class FairmodelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FairmodelVersion
        fields = ('id', 'fairmodel', 'version', 'update_description', 'created_at')

class NewModelVersionData(serializers.Serializer):
    update_type = serializers.ChoiceField(choices=['major', 'minor', 'patch'])
    update_description = serializers.CharField(max_length=255)

    onnx_model = serializers.CharField()
    metadata_id = serializers.CharField(max_length=255)