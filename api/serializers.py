from rest_framework import serializers
from .models import DataType, Fairmodel, FairmodelVersion, VariableLink, VariableType

class FairmodelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fairmodel
        fields = '__all__'
        
class FairmodelVersionSerializer(serializers.ModelSerializer):
    metadata_id = serializers.CharField(required=False, allow_null=True)
    metadata_json = serializers.JSONField(required=False, allow_null=True)

    metadata_input_variables = serializers.JSONField(required=False, allow_null=True)
    metadata_output_variables = serializers.JSONField(required=False, allow_null=True)
    
    model_input_variables = serializers.JSONField(required=False, allow_null=True)
    model_output_variables = serializers.JSONField(required=False, allow_null=True)
    
    has_model = serializers.ReadOnlyField()
    class Meta:
        model = FairmodelVersion
        fields = '__all__'


class VariableLinkSerializer(serializers.ModelSerializer):

    # fairmodel_version = serializers.ForeignKey(FairmodelVersion, on_delete=models.CASCADE)
    variable_type = serializers.ChoiceField(choices=VariableType.choices)

    field_metadata_var_id = serializers.CharField(max_length=255)
    field_model_var_name = serializers.CharField(max_length=255)
    field_model_var_dim_index = serializers.IntegerField(required=False, allow_null=True)
    field_model_var_dim_start = serializers.IntegerField(required=False, allow_null=True)
    field_model_var_dim_end = serializers.IntegerField(required=False, allow_null=True)

    data_type = serializers.ChoiceField(choices=DataType.choices, required=False, allow_null=True)
    # if data_type = category
    categories = serializers.JSONField(required=False, allow_null=True)
    unit = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = VariableLink
        fields = '__all__'


class NewModelVersionData(serializers.Serializer):
    update_type = serializers.ChoiceField(choices=['major', 'minor', 'patch'])
    update_description = serializers.CharField(max_length=255)

    onnx_model = serializers.CharField()
    metadata_id = serializers.CharField(max_length=255)