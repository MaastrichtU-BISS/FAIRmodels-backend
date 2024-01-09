from rest_framework import serializers
from .models import Fairmodel, FairmodelVersion

class FairmodelSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = Fairmodel
        fields = ('id', 'user', 'name', 'description', 'created_at')
class FairmodelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FairmodelVersion
        fields = ('id', 'fairmodel', 'version', 'update_description', 'created_at')

class NewModelVersionData(serializers.Serializer):
    update_type = serializers.ChoiceField(choices=['major', 'minor', 'patch'])
    update_description = serializers.CharField(max_length=255)

    onnx_model = serializers.CharField()
    metadata_id = serializers.CharField(max_length=255)