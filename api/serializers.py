from rest_framework import serializers
from .models import Fairmodel, FairmodelVersion

class FairmodelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fairmodel
        fields = '__all__'
        
class FairmodelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FairmodelVersion
        fields = ('id', 'fairmodel', 'version', 'update_description', 'created_at')

class NewModelVersionData(serializers.Serializer):
    update_type = serializers.ChoiceField(choices=['major', 'minor', 'patch'])
    update_description = serializers.CharField(max_length=255)

    onnx_model = serializers.CharField()
    metadata_id = serializers.CharField(max_length=255)